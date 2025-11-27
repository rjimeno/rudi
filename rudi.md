# Rudi


NAME:

    Rudi - The rudimentary configuration management tool.

    
SYNOPSIS:

```bash
rudi.py [this_nodes_configuration.yaml]
```

If no argument is provided, Rudi will try to open a node configuration file
named `rudi.yaml` in the current working directory and apply it to make the 
current node converge to it.

    
DESCRIPTION:

Rudi is a rudimentary configuration management tool that can be used to 
give a handful of servers some level of configuration. Rudi's configuration 
files are simple YAML files. To learn how to write configuration files we will
start by reading some of them:

```yaml
# This line is a YAML comment. File can be named rudi.yaml
Services:
  apache2:
    packages: [ apache2, php5 ]
    
Packages:
  apache2:
    files: []
  php5:
    files: [ hello.php ]
    
Files:
  hello.php:
    base: /var/www/html/
    name: hello.php
    content: >
      <?php
        header("Content-Type: text/plain");
        echo "Hello, world!\n";
      ?>
    owner: root
    group: root
    mode: "755"
```

The files have four optional elements: Services: Packages:, Files:, and 
Evictions:.

**Note:** 'Packages:' and 'packages:' are different things. The same applies 
to 'Files:' and 'files:'. It is now apparent to the author that it was a poor
choice of names that obfuscates communication and grants some refactoring.

The Services: element is a list of zero or more service names as they appear 
to the `service` command in Ubuntu Linux. Each one of those identifiers, like
`apache2` in the example above, must have exactly one packages: element 
associated to a list with zero or more names of packages that are used by 
the service. In this example, the service `apache2` uses the packages 
`apache2` and `php5` and thus both apper on its list.
 
The Packages: element is a list of zero or more package names as they appear 
to the dpkg command in Ubuntu Linux. In the example 'apache2' and 'php5' 
both represent the packages by the same name. each element has the only 
mandatory element files: that has a list of zero or more unique file 
identifiers (think of them as file names for convenience, but they are not 
exactly the same).
 
The Files: element is a list of zero or more unique file 
identifiers that represent files and, as you might expect, each has a file 
name: that may have the same value as the identifier an forms a fully 
qualified name once joined with the base:.
 
With each identifier in Files: you should also see the owner:, group: and mode:
fields representing each file's metadata. In contrast, the content: field 
represents the actual content of each file.

Finally, there is an Evictions: element associated with a list of zero or 
more package names as they appear to the dpkg command in Ubuntu Linux.

 
INSTALLATION:
 
Rudi is a ~85 line Python script named rudi.py that uses PyYAML and should be 
available from its repository at
[https://github.com/rjimeno/rudi](https://github.com/rjimeno/rudi).
Most Ubuntu Linux 14.04 systems should have Python 3.4 installed. To make 
sure you have PyYAML use ```sapt-get install -y python3-yaml```.

Creating node configuration files for Rudi is simple but not trivial. Start 
by looking into the YAML files in Rudi's repository. Then, check the examples
 in this document and use one of those files and examples as a starting point
 and and make changes according to what you think you will need.
 
Use some free online tool to verify your file is valid YAML
[(like this one)](https://codebeautify.org/yaml-validator)
and use a "disposable" system for testing (i.e. avoid Production 
environments). For simplicity, name the file rudi.yaml but name it 
differently as well. 


USE:

Rudi must be run under the root persona. One way to do it is:
```bash
$ sudo python3 rudi.py
```
but there are many other ways to run it. See the examples below.


EXAMPLES:

 - Invocation:
 
```bash 
$ chmod a+x rudi.py 
$ sudo ./rudi.py  # Implicitly uses rudi.yaml file.
```
  
```bash
# mkdir ~/bin/
# chmod a+x rudi.py
# mv rudi.py ~/bin/
# export PATH=${PATH}:~/bin/
# rudi.py evictCronPhp5Apache2.yaml  # Removes packages cron, php5 & apache2. 
```

- YAML files:

```yaml
# local.yaml
Services:
  apache2:
    packages: [ apache2 ]
# Does not even install anything; just restarts a service.    
```

```yaml
Services:
  cron:
    packages: [ cron ]
Packages:
  cron:
    files: [ crontab ] 
    
Files:
  crontab:
    base: /etc/
    name: crontab
    owner: root
    group: root
    mode: "722"
    content: |
      # Shorter file with the same functionality.
      SHELL=/bin/sh
      PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

      # m h dom mon dow user    command
      17 *    * * *    root    cd / && run-parts --report /etc/cron.hourly
      25 6    * * *    root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
      47 6    * * 7    root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
      52 6    1 * *    root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
      #
```

```yaml
# evictCronPhp5Apache2.yaml
Evictions: [ cron, php5, apache2 ]
```


AUTHOR:

Roberto Jimeno <roberto.jimeno@gmail.com>.


SEE ALSO:
 
bash(1), python(1).


DIAGNOSTICS:

Returns non-zero if more than one node configuration file is provided or there
is a problem while loading it. Warnings are issued when Packages: reference 
files that do not appear under Files:.

 
BUGS:
 
The main "bug" is that Rudi is rudimentary and so the user should not expect 
too much from it. Keep that in mind while reading the rest of this section.

The Evictions feature excesively aggresive. It was created to comply with the
requirement of "[...] provide an abstraction that allows [...] removing 
Debian packages." Not nice. 

If the YAML file has more than one document, only the first one will be used.
Maybe it would make more sense to use them all, but that's still not clear.
 
Rudi could and should perform some sanity checks on the YAML file. For 
example: having a Files: entry that is not used anywhere under Packages: 
should issue warning and require manual intervention before starting (perhaps
 in the form of a Yes/No question.

Most errors are ignored intentionally and with predictable results. This is a 
bug but almost feels like a feature. Regardless, it should be revisited.

Please report any other bugs to the author.
