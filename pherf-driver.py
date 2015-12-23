#!/usr/bin/env python

import argparse, os, sys

#HBASE_DIR=/usr/local/lib/hbase ./bin/pherf-cluster.py -l -drop ALL -scenarioFile ".*user_defined_scenario.xml" -schemaFile ".*user_defined_schema.sql"

def main(**kwargs):
  config_dir = kwargs['config']
  tasks_file = kwargs['tasks']

  assert os.path.isdir(config_dir), "%s is not a directory" % (config_dir)
  assert os.path.isfile(tasks_file), "%s is not a regular file" % (tasks_file)

  with open(tasks_file, 'r') as tasks:
    for task in tasks:
      task = task.strip()
      if not task:
        continue
      
      print 'Running %s' % (task)


if __name__ == '__main__':
  current_dir = os.path.dirname(os.path.realpath(__file__))
  parser = argparse.ArgumentParser()

  parser.add_argument("-t", "--tasks", help="The file containing a list of tasks, one per line, to run as scenario and schema pairs",
      default=os.path.join(current_dir, 'pherf-tasks.txt'))
  parser.add_argument("-c", "--config", help="Path to the pherf configuration directory", default=os.path.join(current_dir,
      'pherf-configs'))

  args = parser.parse_args()
  # convert the arguments to kwargs
  main(**vars(args))
