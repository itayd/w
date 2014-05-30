from os import access, R_OK, W_OK, X_OK
from os.path import abspath, isdir, isfile

from web import notfound, forbidden

from utils import J

class Node(object):
  def __init__(self, path, logger):
    self.__logger = logger
    self.__path = abspath(path)

  @property
  def path(self):
    return self.__path

  @property
  def logger(self):
    return self.__logger

  def __call__(self, method):
    raise NotImplementedError()

  def forbidden(self):
    return forbidden_node(self.path, self.__logger)

class __ForbiddenNode(Node):
  def __init__(self, path, logger):
    Node.__init__(self, path, logger)

  def __call__(self, method):
    forbidden()
    return "forbidden"

def forbidden_node(path, logger):
  return __ForbiddenNode(path, logger)

class __ActualNode(Node):
  def __access(self, flag):
    return access(self.path, flag)

  @property
  def executable(self):
    return self.__access(X_OK)

  @property
  def readable(self):
    return self.__access(R_OK)

  @property
  def writable(self):
    return self.__access(W_OK)

  def _GET(self):
    raise NotImplementedError

  def _PUT(self):
    raise NotImplementedError

  def _POST(self):
    raise NotImplementedError

  def _DELETE(self):
    raise NotImplementedError

  def _INVALID(self):
    forbidden()
    return "Invalid"

  def __call__(self, method):
    return {
      'GET':    self._GET,
      'PUT':    self._PUT,
      'POST':   self._POST,
      'DELETE': self._DELETE
    }.get(method, self._INVALID)()

class __MissingNode(__ActualNode):
  def _POST(self):
    # TODO: maybe write file.
    raise NotImplementedError()

  def _GET(self):
    notfound()
    return "not found"

  def _PUT(self):
    return self._GET()

  def _DELETE(self):
    return self._GET()

def missing_node(path, logger):
  return __MissingNode(path, logger)

class __FileNode(__ActualNode):
  def __init__(self, path, parent, after, logger):
    Node.__init__(self, path, logger)
    self.__after = after
    self.__parent = parent

  def _GET(self):
    return str(self)

  def __str__(self):
    return '%s %s: %s' % (self.__parent, self.path, self.__after)

def file_node(path, parent, afters, logger):
  after = None
  if len(afters) > 0: after = J(*afters)
  assert isfile(path)
  return __FileNode(path, parent, after, logger)

class __DirNode(__ActualNode):
  def _GET(self):
    return str(self)

  def __str__(self):
    return self.path

def dir_node(path, logger):
  return isdir(path) and __DirNode(path, logger) or forbidden_node(path, logger)