__author__ = 'deri'

class NagiosHelper:
    """Help with Nagios specific status string formatting."""
    code = 0
    message_prefixes = {0: 'OK', 1: 'WARNING', 2: 'CRITICAL', 3: 'UNKNOWN'}
    message_text = ''
    performance_data = {}

    def getMessage(self):
        """Build a status-prefixed message with optional performance data generated externally"""
        text = "%s" % self.message_prefixes[self.code]
        if self.message_text:
            text += ": %s" % self.message_text
        if self.performance_data:
            text += "|"
            for label, value in self.performance_data.items():
                text += "'%s'=%s " % (label, value)
        return text

    def setCodeAndMessage(self, code, text):
        self.code = code
        self.message_text = text

    def addPerfdata(self, label, values, warn=None, crit=None, vmin=None, vmax=None):
        """'label'=value[UOM];[warn];[crit];[min];[max]"""
        perfdata = values
        if warn:
            perfdata += ";%s" % warn
        if crit:
            perfdata += ";%s" % crit
        if vmin:
            perfdata += ";%s" % vmin
        if vmax:
            perfdata += ";%s" % vmax
        self.performance_data[label] = perfdata

    def ok(self, text): self.setCodeAndMessage(0, text)
    def warning(self, text): self.setCodeAndMessage(1, text)
    def critical(self, text): self.setCodeAndMessage(2, text)
    def unknown(self, text): self.setCodeAndMessage(3, text)
