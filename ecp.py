#!/usr/bin/env python3

from __future__ import print_function
import requests
import sys
import os
import argparse
import json
import getpass
import datetime
import yaml
import urllib3

class ECP:
  def __init__(self, tokenfile=None, baseurl='https://dev.api.portal.tsi.ebi.ac.uk'):
    self.get_token(tokenfile)
    self.baseurl = baseurl
    urllib3.disable_warnings()

  # gets new token from portal
  def aaplogin(self):
    print('Please visit https://dev.api.aai.ebi.ac.uk/sso and follow the login instructions')
    logged_in = False
    try:
      while not logged_in:
        token = input('Please enter the token received here: ')
        self.set_token(token)
        r = self.make_request('get', 'deployment', '')
        if r.status_code == 401:
          print('Got 401 unauthorized while using token, please verify your token and try again')
        else:
          print('Login successful!')
          logged_in = True
    except KeyboardInterrupt:
      print ('\nNote: On the standard OSX terminal pasting the token might'
             ' hang the process.'
             '\nIf that happens, copy your token to the clipboard and run:'
             '\npbpaste | ecp login\n')
      sys.exit(0)
    with open(os.environ['HOME']+'/.ecp_token', 'w') as tokenfile:
      print(token, file=tokenfile)

  def delete_token(self):
    try:
      os.remove(os.environ['HOME']+'/.ecp_token')
    except OSError as err:
      print ("Error: %s - %s." % (err.filename, err.strerror))

  def set_token(self, token):
    self.token = token
    self.headers = {'Authorization': 'Bearer '+self.token, 'Content-Type': 'application/json'}

  def get_session_token(self):
    return self.token

  def login(self, user='', pw=''):
    if user == '':
      user = input('Please enter your username: ')
    if pw == '':
      pw   = getpass.getpass(prompt = 'Please enter your password: ')
    response = requests.get('https://api.aai.ebi.ac.uk/auth', auth=(user,pw))
    with open(os.environ['HOME']+'/.ecp_token', 'w') as tokenfile:
      print(response.text, file=tokenfile)

    self.set_token(response.text)

    if response.status_code == 200:
      return 'Authorized: 200 OK'
    else:
      return 'Login details incorrect, got status: '+str(response.status_code)

  def get_depl_status(self, depl):
    return requests.get(depl['_links']['status']['href'], headers=self.headers).json()

  # various printing strategies for different resources
  def prettyprint(self, resp, res):
    table = []
    if res == 'deployment' or res == 'deployments':
      if '_embedded' in resp:
        table.append(['REFERENCE','APP NAME', 'STARTED', 'STATUS'])
        for depl in resp['_embedded']['deploymentResourceList']:
          if 'startedTime' in depl:
            ts = depl['startedTime'] / 1000.0
            start_t = datetime.datetime.fromtimestamp(ts).strftime('%H:%M %d-%m-%Y')
          else:
            start_t = ''

          status_r = self.get_depl_status(depl)
          try:
            status = status_r['status']
          except:
            status = 'Error getting status'

          table.append([depl['reference'], depl['applicationName'], start_t, status])

    if res == 'app' or res == 'apps':
      if '_embedded' in resp:
        table.append(['NAME', 'VERSION'])
        for app in resp['_embedded']['applicationResourceList']:
          table.append([app['name'], app['version']])

    if res == 'config' or res == 'configs':
      if '_embedded' in resp:
        for config in resp['_embedded']['configurationResourceList']:
          print('- '+config['name']+':')
          print('    Cloud provider parameters: '+config['cloudProviderParametersName'])
          print('    SSH Public Key: '+config['sshKey'])
          print('    Parameters: '+config['deploymentParametersName'])
        return

    if res == 'sharedconfig' or res == 'sharedconfig':
      if '_embedded' in resp:
        for config in resp['_embedded']['configurationResourceList']:
          print('- '+config['name']+':')
          print('    Cloud provider parameters: '+config['cloudProviderParametersName'])
          print('    Cloud Provider: '+config['cloudProviderType'])
          print('    Parameters: '+config['deploymentParametersName'])
        return

    if res == 'cred' or res == 'creds':
      if '_embedded' in resp:
        for cred in resp['_embedded']['cloudProviderParametersResourceList']:
          print('- '+cred['name']+':')
          print('    Provider: '+cred['cloudProvider'])
          print('    Parameters: ')
          for field in cred['fields']:
            print('    * '+field['key']+': '+field['value'])
        return

    if res == 'param' or res == 'params':
      if '_embedded' in resp:
        for param in resp['_embedded']['configurationDeploymentParametersResourceList']:
          print('- '+param['name']+':')
          print('    Parameters: ')
          for field in param['fields']:
            print('    * '+field['key']+': '+field['value'])
        return

    if len(table) > 0:
      self.print_table(table)
    else:
      # For individual requests, dump to yaml which is better readable
      print(yaml.safe_dump(resp, indent=2, default_flow_style=False))

  def print_table(self, table):
    col_width = max([max(len(str(x)) for x in col) for col in zip(*table)]) + 2
    # assuming square table, can take length of first row
    row_format = len(table[0]) * '{:<{fill}}'
    for row in table:
      print(row_format.format(*row, fill=col_width))

  def get_url(self, resource, name):
    print("In get url", name)
    if resource == 'cred' or resource == 'creds':
      resourcepath = '/cloudproviderparameters/'
    elif resource == 'param' or resource == 'params':
      resourcepath = '/configuration/deploymentparameters/'
    elif resource == 'config' or resource == 'configs':
      resourcepath = '/configuration/'
    elif resource == 'sharedconfig' or resource == 'sharedconfig':
      resourcepath = '/configuration/shared'
    elif resource == 'app' or resource == 'apps':
      resourcepath = '/application/'
    elif resource == 'deployment' or resource == 'deployments':
      resourcepath = '/deployment/'
    elif resource == 'deployment?teamname':
      resourcepath = '/deployment?teamName='
    elif resource == 'logs':
      return self.baseurl+'/deployment/'+name+'/logs'
    elif resource == 'destroylogs':
      return self.baseurl+'/deployment/'+name+'/destroylogs'
    elif resource == 'status':
      return self.baseurl+'/deployment/'+name+'/status'
    elif resource == 'jointeam':
      return self.baseurl+'/team/member'

    try:
      print (self.baseurl+resourcepath+str(name))
      return self.baseurl+resourcepath+str(name)
    except UnboundLocalError:
      print('Unknown verb or resource, try --help for usage', file=sys.stderr)

  # gets token from environment (from previous login)
  def get_token(self, tokenfile=None):
    if tokenfile is not None:
      with open(tokenfile, 'r') as tokenfileh:
        token = tokenfileh.read().replace('\n','')
    elif "ECP_TOKEN" in os.environ:
      token = os.environ["ECP_TOKEN"]
    elif os.path.isfile(os.environ['HOME']+'/.ecp_token'):
      with open(os.environ['HOME']+'/.ecp_token', 'r') as tokenfile:
        token = tokenfile.read().replace('\n','')
    else:
      token = ''

    self.token = token
    self.headers = {'Authorization': 'Bearer '+token, 'Content-Type': 'application/json'}

  def make_request(self, verb, resource, name, data=''):
    if verb == 'create' and resource != 'deployment?teamname':
      name = ''
    url = self.get_url(resource, name)
    if verb == 'get':
      response = requests.get(url, headers=self.headers, verify=False)
    elif verb == 'create':
        response = requests.post(url, headers=self.headers, data=data, verify=False)
    elif verb == 'delete':
      response = requests.delete(url, headers=self.headers, verify=False)
    elif verb == 'stop':
      response = requests.put(url+'/stop', headers=self.headers, verify=False)
    else:
      response = '{}'
      print('Unknown verb, try --help for usage')

    return response

  def print_request(self, response, verb, resource, jsondump):
    try:
      r_json = response.json()
    except:
      #print("Could not decode, raw response:")
      try:
        print('Status '+str(response.status_code)+' '+requests.status_codes._codes[response.status_code][0])
        print(response.text)
      except AttributeError:
        print('printing raw response')
        print(response)

      return

    if jsondump:
      print(json.dumps(r_json, indent=2))
      return

    if verb == 'get':
      self.prettyprint(response.json(), resource)
    else:
      # fallback to yaml as it is more readable by humans
      print(yaml.safe_dump(response.json(), indent=2, default_flow_style=False))

def main(argv):
  parser = argparse.ArgumentParser(description='EBI CLoud Portal CLI')
  parser.add_argument('verb', help='Action to perform on resource, one of: get/create/delete/stop(deployments only)/login')
  parser.add_argument('resource', nargs='?', help='Resource type to perform action on, one of: cred/param/config/app/deployment/deployment?teamname/logs/status')
  parser.add_argument('name', nargs='?', help='Resource name to perform action on; can be omitted for \'get\' action to list all', default='')
  parser.add_argument('--file', '-f', help='File containing JSON to post, use - for stdin')
  parser.add_argument('--token', '-t', help='File containing JWT identity token, is sourced from ECP_TOKEN env var by default')
  parser.add_argument('--json', '-j', help='Print raw JSON responses', action='store_true')
  parser.add_argument('--dev', '-d', help='use dev portal url, https://dev.portal.tsi.ebi.ac.uk', action='store_true')

  arggroup = parser.add_argument_group('login', 'Arguments for \'login\' verb:')
  arggroup.add_argument('--user', '-u', help='Username for local login action (implies -l)', default='')
  arggroup.add_argument('--password', '-p', help='Password for local login action (implies -l)', default='')
  arggroup.add_argument('--local', '-l', help='Use ecp local login', action='store_true')
  arggroup.add_argument('--remove', '-r', help="Delete local token", action='store_true')

  args=parser.parse_args()

  baseurl = 'https://dev.api.portal.tsi.ebi.ac.uk'
  if args.dev:
    baseurl = 'https://dev.api.portal.tsi.ebi.ac.uk'

  e = ECP(baseurl=baseurl)

  if args.file is not None:
    if args.file == '-':
      datafh = sys.stdin
    else:
      datafh = open(args.file, 'r')
    data = datafh.read()
    datafh.close()
  else:
    data = ''

  # convenience method
  # try name arg as file for create action if -f not given
  if args.verb == 'create' and args.file is None:
    try:
      datafh = open(args.name, 'r')
      data = datafh.read()
      datafh.close()
    except:
      print('Error: \'create\' action requires JSON input data (-f)')

  if args.verb == 'login':
    if args.remove:
      e.delete_token()
      return
    if args.local or args.user != '' or args.password != '':
      print(e.login(args.user, args.password), file=sys.stderr)
      return
    else:
      e.aaplogin()
      return

  verbs = ['get','create','delete','stop','login']
  resources = ['cred', 'creds', 'param','params','config','configs', 'sharedconfig', 'app','apps','deployment','deployments','logs','destroylogs', 'status', 'deployment?teamname']
  if not args.verb in verbs:
    print('Unknown verb \''+args.verb+'\', expecting one of: get, create, delete, stop, login', file=sys.stderr)
    return

  # enable 'ecp stop somename' shortcut
  if args.verb == 'stop' and args.resource != 'deployment':
    args.name = args.resource
    args.resource = 'deployment'


  if not args.resource in resources:
    print('Unknown resource \''+str(args.resource)+'\', expecting one of: cred[s], param[s], config[s], app[s], deployment[s], [destroy]logs, status', file=sys.stderr)
    return
  else:
    print("Resource " + args.resource)

  print(args.verb, args.resource, args.name)
  r = e.make_request(args.verb, args.resource, args.name, data=data)
  if r.status_code == 401:
    print('Got 401 unauthorized, please run \'ecp login\' to log in.')
    return
  e.print_request(r, args.verb, args.resource, args.json)

if __name__ == "__main__":
  main(sys.argv)
