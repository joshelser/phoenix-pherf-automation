#!/usr/bin/env python

import argparse, glob, logging, os, shutil, subprocess, sys

logger = logging.getLogger(__name__)

def main(**kwargs):
  validate_args(kwargs)

  current_dir = os.path.dirname(os.path.realpath(__file__))
  phoenix_home = kwargs['phoenix_home']
  phoenix_repo = kwargs['phoenix_repo']
  hbase_home = kwargs['hbase_home']
  hadoop_home = kwargs['hadoop_home']
  maven_installation = kwargs['maven_installation']

  logger.info("Copying phoenix-pherf directory")
  copy_fresh(os.path.join(phoenix_repo, 'phoenix-pherf'), os.path.join(phoenix_home, 'phoenix-pherf'))
  logger.info("Copying pherf-cluster.py")
  copy_fresh(os.path.join(phoenix_repo, 'bin', 'pherf-cluster.py'), os.path.join(phoenix_home, 'bin', 'pherf-cluster.py'))
  logger.info("Copying pherf-configs")
  copy_fresh(os.path.join(current_dir, 'pherf-configs'), os.path.join(phoenix_home, 'bin', 'config'))
  logger.info("Copying phoenix_utils.py")
  copy_fresh(os.path.join(phoenix_repo, 'bin', 'phoenix_utils.py'), os.path.join(phoenix_home, 'bin', 'phoenix_utils.py'))

  # Build and install the phoenix-pherf jars because Ambari doesn't
  build_and_install_pherf_jars(phoenix_repo, phoenix_home, maven_installation)

  # Remove any broken symlinks installed by Ambari
  remove_bad_symlinks(os.path.join(hbase_home, 'lib'))
  remove_bad_symlinks(os.path.join(hadoop_home, 'lib'))

  copy_extra_phoenix_libs(hbase_home, phoenix_home)

  return 0

def validate_args(kwargs):
  phoenix_home = kwargs['phoenix_home']
  phoenix_repo = kwargs['phoenix_repo']
  maven_installation = kwargs['maven_installation']

  # Check that all paths that should be directories are such
  for d in [phoenix_home, phoenix_repo, maven_installation]:
    assert os.path.isdir(d), "%s is not a directory" % (d)

def copy_if_missing(src, dest):
  '''
  Copy the given src to the dest only if dest does not already exist
  '''
  logger.debug("Attempting to copy %s to %s" % (src, dest))
  if not os.path.exists(dest):
    copy(src, dest)
  else:
    logger.debug("Not copying because %s already exists" % (dest))

def copy_fresh(src, dest):
  if os.path.exists(dest):
    logger.debug("Removing %s" % (dest))
    if os.path.isdir(dest):
      shutil.rmtree(dest)
    else:
      os.remove(dest)

  copy(src, dest)

def copy(src, dest):
  '''
  Copy a source to a destination. The source should exist, the destination should not.
  '''
  assert os.path.exists(src), "Source to copy does not exist: '%s'" % (src)
  assert not os.path.exists(dest), "Destination to copy should not exist: '%s'" % (dest)

  if os.path.isdir(src):
    logger.debug("Copying directory %s to %s" % (src, dest))
    shutil.copytree(src, dest)
  else:
    logger.debug("Copying file %s to %s" % (src, dest))
    shutil.copy(src, dest)

def build_and_install_pherf_jars(phoenix_repo, phoenix_home, maven_installation):
  exit_code = subprocess.call([os.path.join(maven_installation, 'bin', 'mvn'), 'package', '-DskipTests'], cwd=phoenix_repo)
  # zero is "false-y"
  if exit_code:
    return exit_code

  jarfiles = glob.glob(os.path.join(phoenix_repo, 'phoenix-pherf', 'target', 'phoenix-pherf*.jar'))
  assert len(jarfiles) > 0, 'Should have found multiple phoenix-perf jars, but found none'
  for jar in jarfiles:
    copy_fresh(jar, os.path.join(phoenix_home, 'lib', os.path.basename(jar)))

  return 0

def remove_bad_symlinks(parent_dir):
  assert os.path.exists(parent_dir) and os.path.isdir(parent_dir), "%s is not a directory" % parent_dir
  for filename in os.listdir(parent_dir):
    full_path = os.path.join(parent_dir, filename)
    # Try to find symlinks to files that don't exist
    if os.path.islink(full_path) and not os.path.exists(full_path):
      logger.info("Removing broken symlink: %s" % full_path)
      os.remove(full_path)

def copy_extra_phoenix_libs(hbase_home, phoenix_home):
  jars_to_link = ['commons-csv-1.0.jar']
  for jar_to_link in jars_to_link:
    source = os.path.join(phoenix_home, 'lib', jar_to_link)
    dest = os.path.join(hbase_home, 'lib', jar_to_link)
    if not os.path.islink(dest):
      logger.debug("Symlinking %s to %s" % (source, dest))
      os.symlink(source, dest)

if __name__ == '__main__':
  current_dir = os.path.dirname(os.path.realpath(__file__))
  logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

  parser = argparse.ArgumentParser()
  parser.add_argument("--phoenix_home", help="The location of the Phoenix installation", default="/usr/hdp/current/phoenix-client/")
  parser.add_argument("--hbase_home", help="The location of the HBase installation", default="/usr/hdp/current/hbase-client/")
  parser.add_argument("--phoenix_repo", help="The location of the Phoenix codebase", default=os.path.join(current_dir, "phoenix"))
  parser.add_argument("--hadoop_home", help="The location of the Hadoop installation", default="/usr/hdp/current/hadoop-client/")
  parser.add_argument('--maven_installation', help="The location of a Maven installation", default=os.path.join(current_dir, 'apache-maven-3.2.5'))

  args = parser.parse_args()
  # convert the arguments to kwargs
  sys.exit(main(**vars(args)))
