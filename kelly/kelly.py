# The single_iter and double_iter objects provide functions that will
# be used in the kfsingle and kfidouble functions below to calculate
# Kelly fractions. These objects are a way of getting around the limit
# in Python that only alows the creation of closures for single line
# functions.


class single_iter(object):
    def __init__(self, rv, pv):
        self.pv = pv
        self.rv = rv

    def f(self, x):
        s1 = s2 = s3 = d1 = d2 = d3 = 0
        for k in range(len(self.pv)):
            pk = self.pv[k]
            rk = self.rv[k]
            d1 = 1 + rk * x
            if d1 == 0:
                d1 = 0.000001
            d2 = rk / d1
            d3 = pk * d2
            s1 += d2
            s2 += d3
            s3 += d2 * d3
        return x - s2 / (s1 * s2 - s3)


class idouble_iter(object):
    def __init__(self, rv1, rv2, pv1, pv2):
        self.pv1 = pv1
        self.rv1 = rv1
        self.pv2 = pv2
        self.rv2 = rv2

    def f(self, v0):
        x = v0[0]
        y = v0[1]
        s1 = s2 = s3 = s4 = s5 = s6 = s7 = d1 = 0
        Rkl = Skl = pklRkl = pklSkl = 0
        for k in range(len(self.pv1)):
            pk = self.pv1[k]
            rk = self.rv1[k]
            for m in range(len(self.pv2)):
                pl = self.pv2[m]
                sl = self.rv2[m]
                d1 = 1 + rk * x + sl * y
                if d1 == 0:
                    d1 = 0.000001
                Rkl = rk / d1
                Skl = sl / d1
                pklRkl = pk * pl * Rkl
                pklSkl = pk * pl * Skl
                s1 += Rkl
                s2 += Skl
                s3 += pklRkl
                s4 += pklSkl
                s5 += pklRkl * Rkl
                s6 += pklSkl * Skl
                s7 += pklRkl * Skl
        fx = s1 * s3 - s5
        fy = s2 * s3 - s7
        gx = s1 * s4 - s7
        gy = s2 * s4 - s6
        det = fx * gy - fy * gx
        dx = (s4 * fy - s3 * gy) / det
        dy = (s3 * gx - s4 * fx) / det
        return [x + dx, y + dy]


def expectation(pv, rv):
    """
    Calculates the return expectation given:
    pv = vector of probabilities
    rv = vector of returns
    The value returned is just the scalar product of the two vectors.
    """
    e = 0
    for i in range(len(pv)):
        e += pv[i] * rv[i]
    return e


def dgsingle(rv, pv, f):
    """
    Evaluates the derivative of the exponential growth factor for
    a single bet.
    rv = vector of returns
    pv = vector of probabilities
    f = bankroll fraction for the bet
    """
    sum = 0.0
    for i in range(len(pv)):
        sum += pv[i] * rv[i] / (1.0 + rv[i] * f)
    return sum


def dgidouble(rv1, rv2, pv1, pv2, f1, f2):
    """
    Evaluates the derivative of the exponential growth factor for
    two independent bets.
    rv1 = vector of returns for bet 1
    rv2 = vector of returns for bet 2
    pv1 = vector of probabilities for bet 1
    pv2 = vector of probabilities for bet 2
    f1 = bankroll fraction for bet 1
    f2 = bankroll fraction for bet 2
    """
    sum1 = sum2 = d = 0
    for i in range(len(rv1)):
        for j in range(len(rv2)):
            d = pv1[i] * pv2[j] / (1.0 + rv1[i] * f1 + rv2[j] * f2)
            sum1 += rv1[i] * d
            sum2 += rv2[j] * d
    return [sum1, sum2]


def kfsingle(rv, pv):
    """
    Calculates the optimal Kelly fraction for a single bet.
    rv = vector of returns
    pv = vector of probabilities
    """
    fiter = single_iter(rv, pv)
    rmax = max(rv)
    rmin = min(rv)
    if rmax <= 0:
        return -1000000.0  # go short to the max
    if rmin >= 0:
        return 1000000.0  # go long to the max

    # set the initial max and min values for x
    if expectation(pv, rv) >= 0:
        xmax = -1.0 / rmin
        xmin = 0.0
        x = xmax / 2.0
    else:
        xmax = 0.0
        xmin = -1.0 / rmax
        x = xmin / 2.0

    # use a simple bisection method to get a tight box around x
    while (xmax - xmin) > 1.0e-8:
        if dgsingle(rv, pv, x) > 0:
            xmin = x
        else:
            xmax = x
        x = (xmax + xmin) / 2.0

    # zero in on x using Newton's method
    x0 = x
    x1 = fiter.f(x)
    while abs(x1 - x0) > 1.0e-10:
        x0 = x1
        x1 = fiter.f(x1)
    return x1


def kfidouble(rv1, rv2, pv1, pv2):
    """
    Calculates the optimal Kelly fraction for two independent
    bets.
    rv1 = vector of returns for bet 1
    rv2 = vector of returns for bet 2
    pv1 = vector of probabilities for bet 1
    pv2 = vector of probabilities for bet 2
    """
    fiter = idouble_iter(rv1, rv2, pv1, pv2)

    # get Kelly fractions for each bet individually
    fs1 = kfsingle(rv1, pv1)
    fs2 = kfsingle(rv2, pv2)

    # if any of the individual fractions is max long or short
    # then we can return immediately
    if abs(fs1) == 1000000.0:
        if abs(fs2) == 1000000.0:
            return [fs1, fs2]
        else:
            return [fs1, 0]
    if abs(fs2) == 1000000.0:
        return [0, fs2]

    # set the initial max and min values for the bet 1 fraction
    if fs1 > 0:
        xmax = fs1
        xmin = 0
    else:
        xmax = 0
        xmin = fs1
    x = fs1 / 2.0

    # set the initial max and min values for the bet 2 fraction
    if fs2 > 0:
        ymax = fs2
        ymin = 0
    else:
        ymax = 0
        ymin = fs2
    y = fs2 / 2.0

    # use a simple bisection method to tighten the box around the
    # optimal x and y values
    while ((xmax - xmin) > 1.0e-8) and ((ymax - ymin) > 1.0e-8):
        fv = dgidouble(rv1, rv2, pv1, pv2, x, y)
        if fv[0] > 0:
            xmin = x
        else:
            xmax = x
        if fv[1] > 0:
            ymin = y
        else:
            ymax = y
        x = (xmax + xmin) / 2.0
        y = (ymax + ymin) / 2.0

    # zero in on x and y with Newton's method
    v0 = [x, y]
    v1 = fiter.f([x, y])
    while abs(v1[0] - v0[0]) > 1.0e-10 or abs(v1[1] - v0[1]) > 1.0e-10:
        v0 = v1
        v1 = fiter.f(v1)
    return v1
