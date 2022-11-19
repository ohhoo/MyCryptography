#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sm4_tool.py
@Time    :   2022/11/14 21:07:36
@Author  :   XuDong
'''
#该文件中实现SM4算法中将会用到的基础运算，如移位、填充

def data_left_shift(data:int, num:int) -> int:
    '''完成数据的移位操作
    将传入的数据data二进制形式循环移动num位,得到移位后的int型数据
    Args:
        data(int) : 需要进行移位操作的16进制无符号数
        num(int) : 需要移动的位数
    Return:
        int : 返回移位操作的结果
    '''
    return ((data << num) & 0xFFFFFFFF) | ((data >> (32-num)) & 0xFFFFFFFF)


def padding_zeros(data:bytes, num=128) -> bytes:
    '''对数据进行填充
    对数据进行填充,填充至num所标明的位数(该位数为bit位数),
    填充的内容为b'\x00'即ascii码中的空(转换为数字是0),填充的位置为bytes串的左侧, 
    num不符合规定(小于data位数、或不为8的倍数)或data为空，返回空串
    Args:
        data(bytes) : 需要进行填充的bytes串
        num(int)    : 数据应有的长度
    Returns:
        bytes : 返回填充后的bytes串
    '''
    if len(data) == 16:
        return data
    
    pad = b'\x00' * (int(num/8) - len(data))
    
    return pad + data
    

if __name__ == "__main__":
    a = b'hello'
    b = b'world'
    c = padding_zeros(a, 32)
    print(c)