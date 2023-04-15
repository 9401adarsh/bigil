import hashlib

class PCProver:
    def __init__(self, g=5, p=2333, s=15):
        self.g = g
        self.q = 2*p + 1
        self.s = s
        self.h = pow(g, s, self.q)
    def commit(self, M, r):
        m = int(hashlib.sha256(M.encode()).hexdigest() ,16)
        c = pow(self.g, m, self.q) * pow(self.h, r, self.q) % self.q
        return (Message(M, r), Commitment(c))
    def getParams(self):
        return PCParameters(self.q, self.g, self.h)

class Message:
    def __init__(self, M, r):
        self.M = M
        self.r = r
    def __repr__(self):
        return """M | {}
r | {}""".format(self.M, self.r)

class Commitment:
    def __init__(self, c):
        self.c = c
    def __repr__(self):
        return """c | {}""".format(self.c)

class PCParameters:
    def __init__(self, q, g, h):
        self.q = q
        self.g = g
        self.h = h

class PCVerifier:
    def __init__(self, params):
        self.c = []
        self.m = []
        self.r = []
        self.q = params.q
        self.g = params.g
        self.h = params.h
    def __repr__(self):
        returnStr = """Commitments | {}
Messages    | {}
q           | {}
g           | {}
h           | {}""".format(len(self.c), len(self.m), self.q, self.g, self.h)
        return returnStr
    def add(self, dataObject):
        if(type(dataObject) is Commitment):
            self.c.append(dataObject.c)  
        if(type(dataObject) is Message):
            m = int(hashlib.sha256(dataObject.M.encode()).hexdigest() ,16)
            self.m.append(m)
            self.r.append(dataObject.r)
    def productCommitments(self):
        pi = 1
        for ci in self.c:
            pi *= ci
        return pi % self.q
    def verify(self):
        c = self.productCommitments()
        m_sum = 0
        r_sum = 0
        for i in range(len(self.m)):
            m_sum += self.m[i]
            r_sum += self.r[i]
        cv = pow(self.g, m_sum, self.q) * pow(self.h, r_sum, self.q) % self.q
        return c == cv

