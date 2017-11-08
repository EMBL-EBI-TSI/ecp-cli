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

Examples:
`ecp get param`
`ecp create config -f config.json`
`ecp delete app myapp`
