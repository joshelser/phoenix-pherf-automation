#!/usr/bin/env python

import argparse, glob, logging, os, subprocess, sys

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

      print ""
      for driver in ["thick", "thin"]:
        logger.info("Running pherf over scenario/schema using %s driver: '%s'" % (driver, task))
        exit_code = run_task(task, kwargs, queryserver=(driver == "thin"))
        if exit_code != 0:
          logger.warn("Saw non-zero exit code (%d) when running %s" % (exit_code, task))
          return exit_code

  summarize_results(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'RESULTS'))

  return 0

def validate_args(kwargs):
  config_dir = kwargs['config']
  tasks_file = kwargs['tasks']
  hbase_home = kwargs['hbase_home']
  phoenix_home = kwargs['phoenix_home']

  for d in [config_dir, hbase_home, phoenix_home]:
    assert os.path.isdir(d), "%s is not a directory" % (d)
  assert os.path.isfile(tasks_file), "%s is not a regular file" % (tasks_file)


def run_task(task, kwargs, queryserver=False):
  env = os.environ.copy()
  # Why HBASE_DIR and not HBASE_HOME? :shrug:
  env['HBASE_DIR'] = kwargs['hbase_home']

  # Make sure we can find pherf-cluster.py to run
  pherf_cluster_script = os.path.join(kwargs['phoenix_home'], 'bin', 'pherf-cluster.py')
  assert os.path.isfile(pherf_cluster_script), 'Could not find pherf-cluster.py script at %s' % pherf_cluster_script

  arguments = [pherf_cluster_script, '-l', '-drop', 'ALL', '-stats', '-q',
      '-scenarioFile', '".*%s_scenario.xml"' % task, '-schemaFile', '".*%s_schema.sql"' % task]
  if queryserver:
    queryserver_url = kwargs["queryserver_url"]
    assert queryserver_url, "The QueryServer URL must be provided"
    arguments.append("-t")
    arguments.append("-s")
    arguments.append(queryserver_url)
  exitcode = subprocess.call(arguments, env=env)

  return exitcode

def summarize_results(results_dir):
  assert os.path.isdir(results_dir), "%s is not a directory"
  print "Data load summary:"
  for f in glob.glob(os.path.join(results_dir, "RESULT_Data_Load_Summary*")):
    results_file = os.path.join(results_dir, f)
    print "\nResults for %s" % (results_file)
    with open(results_file, 'r') as fh:
      for line in fh:
        print line.rstrip()

  print "\n\nQuery summary:"
  for f in glob.glob(os.path.join(results_dir, "RESULT_COMBINED*")):
    results_file = os.path.join(results_dir, f)
    print "\nResults for %s" % (results_file)
    with open(results_file, 'r') as fh:
      for line in fh:
        print line.rstrip()

if __name__ == '__main__':
  current_dir = os.path.dirname(os.path.realpath(__file__))
  logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
  parser = argparse.ArgumentParser()

  parser.add_argument("-t", "--tasks", help="The file containing a list of tasks, one per line, to run as scenario and schema pairs",
      default=os.path.join(current_dir, 'pherf-tasks.txt'))
  parser.add_argument("-c", "--config", help="Path to the pherf configuration directory", default=os.path.join(current_dir,
      'pherf-configs'))
  parser.add_argument("--queryserver_url", help="The URL of the Phoenix QueryServer", default="http://localhost:8765")
  parser.add_argument("--hbase_home", help="The location of the HBase installation", default="/usr/hdp/current/hbase-client/")
  parser.add_argument("--phoenix_home", help="The location of the Phoenix installation", default="/usr/hdp/current/phoenix-client/")

  args = parser.parse_args()
  # convert the arguments to kwargs
  sys.exit(main(**vars(args)))
