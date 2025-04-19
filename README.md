# beancount-repete

This is a [beancount plugin](https://beancount.github.io/docs/beancount_scripting_plugins.html) that allows specific Transactions to be marked as templates, and repeated on a schedule. The plugin generates synthetic Transactions that mirror their template precisely, with two exceptions:

- the generated Transactions' dates are changed, in line with the set of dates that the template's schedule produces;
- the metadata pair that triggers the plugin (and holds the schedule) is removed. This allows the output of the plugin to be used safely as input for the plugin, without generating unlimited/runaway Transactions.

The schedule can be expressed in any natural language form that the [Recurrent](https://github.com/kvh/recurrent#examples) library supports.

Any Transaction used as a template is removed by the plugin during processing. This allows for schedules such as "monthly from next tuesday" to be used, where the "now" date is taken as being the template Transaction's date.

## Installation

### Using pip

Use pip to install the package:

```shell
pip install git+https://github.com/jpluscplusm/beancount-repete
```

Add this line to your beancount file to enable the plugin:

```
plugin "beancount_repete"
```

## Usage

Add a metadata pair to any Transaction, with key `repete` and a value holding the natural language expression of a repeating (or one-off!) schedule. The schedule is parsed by the [Recurrent](https://github.com/kvh/recurrent) library, whose [documentation](https://github.com/kvh/recurrent#examples) shows many examples of the text forms that it understands.

### Examples

Given this `example.beancount` input, and the beancount-repete plugin (set up as above):

```shell
$ cat example.beancount

plugin "beancount_repete"
plugin "beancount.plugins.auto_accounts"

2022-01-01 ! "Supermarket" "Weekly shop"
  repete: "weekly until March 2022"
  Assets:Current:Bank:HSBC
  Expenses:Groceries:Weekly   75.00 GBP
```

... the following journal is visible to beancount and any of its tools (e.g. Fava, bean-query, etc):

```shell
$ bean-report example.beancount print
2022-01-01 open Assets:Current:Bank:HSBC
2022-01-01 open Expenses:Groceries:Weekly

2022-01-01 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-01-08 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-01-15 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-01-22 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-01-29 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-05 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-12 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-19 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-26 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

```

Note that the template Transaction's flag (`!`, here) is persisted across into the synthetic Transactions. It's a good idea to use the "pending" `!` flag, so that Fava and other interfaces don't indicate that this is an entirely normal, concrete Transaction.

The date of the template Transaction is used as the "now" date when interpreting the schedule, which can be useful when the schedule is relative in some way. For example ...

January 1, 2022 was a Saturday. If the above example schedule is modified slightly, we can see the effect:

```shell
$ cat example.beancount
option "insert_pythonpath" "True"

plugin "plugins.beancount-repete.plugin"
plugin "beancount.plugins.auto_accounts"

2022-01-01 ! "Supermarket" "Weekly shop"
  repete: "weekly on Tuesday until March 2022"
  Assets:Current:Bank:HSBC
  Expenses:Groceries:Weekly   75.00 GBP

$ bean-report example.beancount print
2022-01-04 open Assets:Current:Bank:HSBC
2022-01-04 open Expenses:Groceries:Weekly

2022-01-04 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-01-11 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-01-18 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-01-25 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-01 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-08 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-15 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-02-22 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP

2022-03-01 ! "Supermarket" "Weekly shop"
  Assets:Current:Bank:HSBC   -75.00 GBP
  Expenses:Groceries:Weekly   75.00 GBP
```

Note that the original template, on 2022-01-01, is not present in this output. This is always true: if a template's schedule would not generate its original date when evaluated, the template Transaction will not be produced.

### Limit

There will be no entries generated that fall past the limit given by the option *repeat_limit*. This option can be specified in the same syntax as for the `repete:` entry metadata shown above. The default is "in one year". Contrary to the entry metadata, this time point is resolved using the current time as reference.

For example, if you want no repeting transactions to be generated that lie in the future, you can change the plugin load statement in your beancount file like this:

```
plugin "plugins.beancount-repete" "repeat_limit=tomorrow"
```

## Installation into beancount repository 

As an alternative to the default install method, you can copy the files of this plugin directly into the folder of your beancount file. Use the beancount option `insert_pythonpath` in this case. To access a subfolder, prepend it and separate with a dot, like for Python modules.

This is how the setup of the author currently looks like:

```shell
$ grep pythonpath main.beancount 
option "insert_pythonpath" "True"
$ grep repete main.beancount 
plugin "plugins.beancount-repete"
$ cd plugins
$ git submodule add https://github.com/jpluscplusm/beancount-repete
Cloning into 'beancount-repete'...
remote: Enumerating objects: 6, done.
remote: Counting objects: 100% (6/6), done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 6 (delta 0), reused 3 (delta 0), pack-reused 0
Receiving objects: 100% (6/6), 12.65 KiB | 762.00 KiB/s, done.
```

When using this method, you have to install dependencies manually:

Install the [Recurrent](https://github.com/kvh/recurrent) library. It is available [from PyPI](https://pypi.org/project/recurrent/).

