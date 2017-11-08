# ECP Command Line Client

An ECP command line client, make executable and stick it in your path.

Get an ECP token, stick it in a file and use the --token (-t) flag to pass it. 
Or export it to the `ECP_TOKEN` environment variable.

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

Use the --file (-f) flag to pass json for the create action

Examples:

`ecp get param`

`ecp create config -f config.json`

`ecp delete app myapp`

`ecp get cred -t tokenfile.jwt`
