import imp
import os

from PyQt4.QtCore import pyqtSignal, QProcess, QObject, QProcessEnvironment


class SyncProvider(QObject):
    syncComplete = pyqtSignal()
    syncStarted = pyqtSignal()
    syncMessage = pyqtSignal(str)
    syncError = pyqtSignal(str)
    syncFinished = pyqtSignal()

    def __init__(self, name, project):
        super(SyncProvider, self).__init__(None)
        self._name = name
        self.closeproject = False
        self.project = project

    @property
    def name(self):
        return self._name

    def startSync(self):
        pass

    def getReport(self):
        return "<p>No report for sync provider generated<p>"


class BatchFileSync(SyncProvider):
    def __init__(self, name, project, **kwargs):
        super(BatchFileSync, self).__init__(name, project)
        self.cmd = kwargs['cmd']
        if self.project:
            self.rootfolder = os.path.abspath(self.project.folder)
        else:
            self.rootfolder = kwargs['rootfolder']

        self.project = project
        self.closeproject = kwargs.get("close_project", False)
        self.process = QProcess()
        self.parser = kwargs.get("parser", None)
        self.parsermodule = None
        variables = kwargs.get("variables", {})
        env = QProcessEnvironment.systemEnvironment()
        for varname, value in variables.iteritems():
            env.insert(varname, str(value))
        self.process.setProcessEnvironment(env)
        self.process.setWorkingDirectory(os.path.dirname(os.path.realpath(self.cmd)))
        self.process.finished.connect(self.complete)
        self.process.started.connect(self.syncStarted)
        self.process.readyReadStandardError.connect(self.error)
        self.process.readyReadStandardOutput.connect(self.readOutput)
        self._output = ""
        self.haserror = False

    def import_parser_module(self):
        import imp
        name = self.parser
        module = imp.find_module(name, [self.rootfolder])
        module = imp.load_module(name, *module)
        self.parsermodule = module
        print self.parsermodule

    def start(self):
        if not self.parsermodule and self.parser:
            self.import_parser_module()

        self._output = ""
        self.haserror = False
        self.process.start(self.cmd, [])

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self._output = value

    def error(self):
        self.haserror = True

    def complete(self, error, status):
        if error > 0 or self.haserror:
            stderr = self.process.readAllStandardError().data()
            self.syncError.emit(stderr)
        else:
            self.syncComplete.emit()
        self.syncFinished.emit()

    def readOutput(self):
        output = str(self.process.readAll())
        ok = True
        if self.parsermodule:
            ok, output = self.parsermodule.sync_output(output)

        if not ok:
            self.haserror = True
            self.process.kill()
            self.syncError.emit(output)
        else:
            self.syncMessage.emit(output)
