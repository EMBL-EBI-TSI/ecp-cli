# ECP Command Line Client

An ECP command line client, make executable and stick it in your `PATH`.

Get an ECP token, stick it in a file and use the --token (-t) flag to pass it. 
Or export it to the `ECP_TOKEN` environment variable.

## Synopsis

Main commands are run as `ecp *action* *resource* [*name*]`
Actions are: 
 - get
 - create
 - delete

Resources are: 
 - cred
 - param
 - config
 - app
 - deployment
 - logs

Use the --file (-f) flag to pass json for the create action

## Examples

`ecp get param`

`ecp create config -f config.json`

`ecp delete app myapp`

`ecp get logs TSI1310559760601 -t tokenfile.jwt`
