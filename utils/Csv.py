import codecs
import cStringIO
from logs.LogManager import LogManager

__author__ = 'Tuly'

import csv


class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class Csv:
    def __init__(self, fileName=None):
        self.logger = LogManager(__name__)
        if fileName is not None:
            self.writer = UnicodeWriter(open(fileName, 'ab'), quoting=csv.QUOTE_ALL)

    def writeCsvRow(self, data):
        try:
            self.writer.writerow(data)
        except Exception, x:
            self.logger.error(x)

    def readCsvRow(self, fileName, rowIndex=-1):
        rows = []
        try:
            reader = csv.reader(open(fileName, 'rb'))
            if rowIndex > -1:
                for row in reader:
                    rows.append(row[rowIndex])
            else:
                for row in reader:
                    rows.append(row)

        except Exception, x:
            self.logger.error(x)
        return rows
