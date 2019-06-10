###############################################
# (c) 2019 FLARM Technology Ltd.
# CONFIDENTIAL - For internal use only. Do not distribute.
###############################################

import math


def _raw_iterator(data_in):
    for pos in range(len(data_in)):
        data = ord(data_in[pos])
        if data < 38:
            data -= 1
        else:
            data -= 58
        yield (pos, data)


def _decode_lfla(data_in, format):
    raw = _raw_iterator(data_in)
    res = []
    old = 56
    for fmt in format:
        r = 0
        mult = 1
        for _ in range(fmt):
            (pos, current) = next(raw)
            r |= ((current ^ old) ^ pos) * mult
            old = current
            mult *= (1 << 6)
        if (r & (mult >> 1)) > 0:
            r -= mult
        res.append(r)
    return res


def decode_lfla_rx(line):
    ''' Decoder for RX data.
    '''
    data = _decode_lfla(line, [5, 3, 3, 3, 3, 3, 2, 2, 2, 2])

    north = data[1]
    east = data[2]
    my_track_rad = float(data[4]) / 10.0 / 180.0 * math.pi
    res = [('his_ID', "{:X}".format(data[0])),
           ('ned', [north, east, -data[3]]),
           ('his_track', data[6])]
    return dict(res)


_test_lfla = '''
LFLA114441EE0BDbcrsrsA?A?A?A?A?A?srrsSSrsA?
LFLA114441EE1A?rstutursA?A?A?A?A?srA?rssrVV
LFLA114441EE2A?tuA?rsA?ddppff`aA?A?rsrsA?A?
LFLA114441EE3A?A?rs
LFLA11444502;GL`Z#rySvpXXMatd>c?tfqZt]s#
LFLA11445102;GL`Zu`[@b#BB?ncsQtPew`kbkej
LFLA11445202WQGsyaJQ<TiQI<EQAQ?PKAVELEKD
LFLA11445902;GL`Zx]%lSMHH=taqRoS[qfu[r#s
LFLA11445903tutsdich`PPWJW
LFLA11450102WQGsyaJQA=p#tqbn%q_pis#oipfq
LFLA11450802WQGsyEwtxwBu%catd:g;[pgt]tZu
LFLA11451202WQGsyaKPOOZ?TQEP@b?cCX?LBKEJ
LFLA11451402;GL`ZpdgOD:Zad<VF`Eahr]ngnho
'''.strip()


if __name__ == '__main__':
    from pprint import pprint
    for line in _test_lfla.split('\n'):
        if('02' == line[10:12]):
            pprint(decode_lfla_rx(line[12:]))
