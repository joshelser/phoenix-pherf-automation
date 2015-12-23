#!/usr/bin/env python

import argparse, logging, os, subprocess, sys

#HBASE_DIR=/usr/local/lib/hbase ./bin/pherf-cluster.py -l -drop ALL -scenarioFile ".*user_defined_scenario.xml" -schemaFile ".*user_defined_schema.sql"

logger = logging.getLogger(__name__)

def main(**kwargs):
  validate_args(kwargs)

  with open(kwargs['tasks'], 'r') as tasks:
    for task in tasks:
      task = task.strip()
      if not task:
        logger.debug('Skipping whitespace-only task')
        continue

      logger.info("Running pherf over scenario/schema: '%s'" % (task))
      exit_code = run_task(task, kwargs)
      if exit_code != 0:
        logger.warn("Saw non-zero exit code (%d) when running %s" % (exit_code, task))
        return exit_code

  return 0

def validate_args(kwargs):
  config_dir = kwargs['config']
  tasks_file = kwargs['tasks']
  hbase_home = kwargs['hbase_home']
  phoenix_home = kwargs['phoenix_home']

  for d in [config_dir, hbase_home, phoenix_home]:
    assert os.path.isdir(d), "%s is not a directory" % (d)
  assert os.path.isfile(tasks_file), "%s is not a regular file" % (tasks_file)


def run_task(task, kwargs):
  env={}
  # Why HBASE_DIR and not HBASE_HOME? :shrug:
  env['HBASE_DIR'] = kwargs['hbase_home']

  # Make sure we can find pherf-cluster.py to run
  pherf_cluster_script = os.path.join(kwargs['phoenix_home'], 'bin', 'pherf-cluster.py')
  assert os.path.isfile(pherf_cluster_script), 'Could not find pherf-cluster.py script at %s' % pherf_cluster_script

  exitcode = subprocess.call([pherf_cluster_script, '-l', '-drop', 'ALL', '-stats',
      '-scenarioFile', '".*%s_scenario.xml"' % task, '-schemaFile', '".*%s_scenario.sql"' % task], env=env)

  return exitcode

if __name__ == '__main__':
  current_dir = os.path.dirname(os.path.realpath(__file__))
  logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
  parser = argparse.ArgumentParser()

  parser.add_argument("-t", "--tasks", help="The file containing a list of tasks, one per line, to run as scenario and schema pairs",
      default=os.path.join(current_dir, 'pherf-tasks.txt'))
  parser.add_argument("-c", "--config", help="Path to the pherf configuration directory", default=os.path.join(current_dir,
      'pherf-configs'))
  parser.add_argument("--thin", help="Use the Phoenix Thin Driver", default=False)
  parser.add_argument("--hbase_home", help="The location of the HBase installation", default="/usr/hdp/current/hbase-client/")
  parser.add_argument("--phoenix_home", help="The location of the Phoenix installation", default="/usr/hdp/current/phoenix-client/")

  args = parser.parse_args()
  # convert the arguments to kwargs
  sys.exit(main(**vars(args)))
