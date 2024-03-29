> **Note**
> The EBI Cloud Portal has been retired and its code base is no longer updated. If you would like to contact the Cloud Portal authors, please leave us feedback via [the EBI contact form](https://www.ebi.ac.uk/about/contact/support/other) mentioning the EBI Cloud Portal in the Subject.

# ECP Command Line Client

An ECP command line client, make executable and stick it in your `PATH`.

First run `ecp login` to log in through Elixir AAI, your token will be stored automatically. 

_Note: On the standard OSX terminal pasting in your token might hang the process. If that happens, login to https://api.aai.ebi.ac.uk/sso, copy your token to the clipboard and run `pbpaste | ecp login`._

If you want to use a token from a different source,
stick it in a file and use the `--token` (`-t`) flag to pass it. 
Or export it to the `ECP_TOKEN` environment variable.

## Synopsis

Main commands are run as `ecp *action* *resource* [*name*]`. Leave out the name for `get` actions to get the full list of that resource.
Actions are: 
 - get
 - create
 - delete
 - stop (deployments only)
 - login

Resources are: 
 - cred
 - param
 - config
 - app
 - deployment
 - logs
 - destroylogs
 - status

Plurals are allowed for readability purposes e.g. `ecp get params` to list all parameters.
Use the `--file` (`-f`) flag to pass JSON data for the create action.

## Examples

List all parameters available:

`ecp get params`

Create a cloud configuration described in config_example.json:

`ecp create config -f examples/config_example.json`

Delete the app named 'My App':

`ecp delete app 'My App'`

Get logs for deployment TSI1310559760601 using a custom tokenfile:

`ecp get logs TSI1310559760601 -t tokenfile.jwt`

## Side notes for Mac OS X

The `python3` is required. Installed it with:

`brew install python3`

if needed.  

It is a good idea to keep the default version unchanged.

Modules `requests` and `yaml` are not installed by default. Run:

`sudo pip3 install requests`

and

`sudo pip3 install pyyaml`

as necessary.
