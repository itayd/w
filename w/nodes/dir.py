from os.path import isdir, isfile

from actual import ActualNode
from static import StaticNode
from cgi import CGINode
from missing import MissingNode
from forbidden import ForbiddenNode

from os import access, X_OK

from ..utils import S, J

def node(path, parent):
  if isdir(path):
    node_type = DirNode
  elif isfile(path):
    if access(path, X_OK):
      node_type = CGINode
    else:
      node_type = StaticNode
  else:
    node_type = MissingNode

  return node_type(path, parent)

class DirNode(ActualNode):
  def _GET(self):
    return str(self)

  def __str__(self):
    return self.path

  def resolve(self, path):
    if path is None: return self

    head, rest = S(path)

    if head == '': return self.resolve(rest)

    next_path = J(self.path, head)
    if head == '..': return ForbiddenNode(next_path, self)

    next_node = node(next_path, self)
    return next_node.resolve(rest)