#!/usr/bin/env python

import argparse, logging, os, shutil, sys

logger = logging.getLogger(__name__)

def main(**kwargs):
  validate_args(kwargs)

  current_dir = os.path.dirname(os.path.realpath(__file__))
  phoenix_home = kwargs['phoenix_home']
  phoenix_repo = kwargs['phoenix_repo']

  logger.info("Copying pherf-cluster.py")
  copy_if_missing(os.path.join(phoenix_repo, 'bin', 'pherf-cluster.py'), os.path.join(phoenix_home, 'bin', 'pherf-cluster.py'))
  logger.info("Copying phoenix-pherf directory")
  copy_if_missing(os.path.join(phoenix_repo, 'phoenix-pherf'), os.path.join(phoenix_home, 'phoenix-pherf'))

  logger.info("Copying pherf-configs")
  copy_fresh(os.path.join(current_dir, 'pherf-configs'), os.path.join(phoenix_home, 'bin', 'configs'))

  return 0

def validate_args(kwargs):
  phoenix_home = kwargs['phoenix_home']
  phoenix_repo = kwargs['phoenix_repo']

  # Check that all paths that should be directories are such
  for d in [phoenix_home, phoenix_repo]:
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

if __name__ == '__main__':
  current_dir = os.path.dirname(os.path.realpath(__file__))
  logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

  parser = argparse.ArgumentParser()
  parser.add_argument("--phoenix_home", help="The location of the Phoenix installation", default="/usr/hdp/current/phoenix-client/")
  parser.add_argument("--phoenix_repo", help="The location of the Phoenix codebase", default=os.path.join(current_dir, "phoenix"))

  args = parser.parse_args()
  # convert the arguments to kwargs
  sys.exit(main(**vars(args)))
