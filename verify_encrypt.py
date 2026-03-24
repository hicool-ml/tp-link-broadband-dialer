#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 TP-Link 密码加密算法
"""

def org_auth_pwd(pwd: str) -> str:
    key = "RDpbLfCPsJZ7fiv"
    char_map = ("yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW")

    result = ""
    k = 187
    l = 187

    f = len(pwd)
    g = len(key)
    h = len(char_map)
    e = max(f, g)

    for m in range(e):
        k = 187
        l = 187

        if m >= f:
            l = ord(key[m])
        elif m >= g:
            k = ord(pwd[m])
        else:
            k = ord(pwd[m])
            l = ord(key[m])

        index = (k ^ l) % h
        result += char_map[index]

    return result


# 测试
plaintext = "Cdu@123"
encrypted = org_auth_pwd(plaintext)

print(f"明文: {plaintext}")
print(f"加密结果: {encrypted}")
print(f"期望结果: Qa0xrnYc9TefbwK")
print(f"验证: {'PASS' if encrypted == 'Qa0xrnYc9TefbwK' else 'FAIL'}")
