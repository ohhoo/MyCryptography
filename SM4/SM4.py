#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   SM4.py
@Time    :   2022/11/13 23:48:25
@Author  :   XuDong
'''
from sm4_tool import padding_zeros, data_left_shift


class SM4Crypto(object):
    '''
    SM4加解密类
    '''
    
    # 16 * 16 的查找表
    __SBox = [
        [0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05],
        [0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99],
        [0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62],
        [0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6],
        [0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8],
        [0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb, 0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35],
        [0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25, 0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87],
        [0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52, 0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e],
        [0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1],
        [0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3],
        [0x1d, 0xf6, 0xe2, 0x2e, 0x82, 0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f],
        [0xd5, 0xdb, 0x37, 0x45, 0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51],
        [0x8d, 0x1b, 0xaf, 0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8],
        [0x0a, 0xc1, 0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0],
        [0x89, 0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84],
        [0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39, 0x48]
    ]

    #系统参数，用于生成密钥
    __FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]
    
    #固定参数，用于生成密钥
    __CK = [
        0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
        0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
        0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
        0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
        0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
        0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
        0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
        0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
    ]
    
    def __init__(self, key:bytes) -> None:
        self.key = padding_zeros(key, 128)
        self.round_key = None
        
    def expansion_key(self) ->None:
        '''密钥拓展算法
        将128bit的主密钥拓展为32个32bit的密钥，分别用于SM4的32轮加解密
        
        '''
        #开始密钥拓展运算
        self.round_key = [0] * 32
        Ki = [0] * 36
        
        #与FK进行异或
        Ki[0] = int(self.key[:4].hex(), 16) ^ SM4Crypto.__FK[0]
        Ki[1] = int(self.key[4:8].hex(), 16) ^ SM4Crypto.__FK[1]
        Ki[2] = int(self.key[8:12].hex(), 16) ^ SM4Crypto.__FK[2]
        Ki[3] = int(self.key[12:].hex(), 16) ^ SM4Crypto.__FK[3]
        
        for i in range(0, 32):
            temp = self.linear_transform(self.sbox_32(Ki[i+1] ^ Ki[i+2] ^ Ki[i+3] ^ SM4Crypto.__CK[i]))
            self.round_key[i] = Ki[i] ^ temp
            Ki[i+4] = Ki[i] ^ temp
        
        
    def sbox(self, data:int) -> int:
        '''查询s盒操作
        Args:

        '''
        row = (data & 0xF0) >> 4
        column = (data & 0x0F)
        return SM4Crypto.__SBox[row][column]
        
    def sbox_32(self, data:int) -> int:
        '''
        32位数字查询s盒
        '''
        mid = []
        for i in range(4):
            temp = self.sbox(data & 0x000000FF)
            mid.insert(0, temp)
            data = data >> 8
        
        mid = ['%02x' % i for i in mid]
        result = ''.join(mid)
        
        return int(result, 16)
        
    def linear_transform(self, data:int, mode=1) -> int:
        '''执行线性变换
        移位异或操作
        '''
        #mode 1 表示密钥拓展算法中的线性变换
        if mode == 1:
            return data ^ (data_left_shift(data, 13)) ^ (data_left_shift(data, 23))
        elif mode == 2:
            return data ^ (data_left_shift(data, 2)) ^ (data_left_shift(data, 10)) ^ (data_left_shift(data, 18)) ^ (data_left_shift(data, 24))
        
    def encryption(self, data:bytes) ->bytes:
        '''执行加密操作
        对明文数据进行加密，返回加密后的数据，采用的密钥为类型成员key
        Args:
            data(bytes) : 明文数据
        Returns:
            bytes : 加密后的数据
        ''' 
        if not self.round_key:
            self.expansion_key()
        
        data = padding_zeros(data, 128)
        middle = [0] * 36
        
        middle[0] = int(data[:4].hex(), 16)
        middle[1] = int(data[4:8].hex(), 16)
        middle[2] = int(data[8:12].hex(), 16)
        middle[3] = int(data[12:16].hex(), 16)
        
        #轮函数，一共32轮
        for i in range(0,32):
            temp = self.linear_transform(self.sbox_32(middle[i + 1] ^ middle[i + 2] ^ middle[i+3] ^ self.round_key[i]),2)
            middle[i+4] = middle[i] ^ temp
        
        result = ''
        for i in range(35, 31, -1):
            result += '%08x' % middle[i]
        
        return bytes.fromhex(result)
    
    def decryption(self, data:bytes) -> bytes:
        '''解密数据
        对加密的数据利用当前的密钥进行解密,解密的流程与加密相同，不过是将轮密钥逆序使用
        Args:
            data(bytes) : 加密后的数据
        Return:
            bytes : 解密后的数据
        '''
        if not self.round_key:
            self.expansion_key()
            
        middle = [0] * 36
        
        middle[0] = int(data[:4].hex(), 16)
        middle[1] = int(data[4:8].hex(), 16)
        middle[2] = int(data[8:12].hex(), 16)
        middle[3] = int(data[12:16].hex(), 16)
        
        #轮函数，一共32轮
        for i in range(0,32):
            temp = self.linear_transform(self.sbox_32(middle[i + 1] ^ middle[i + 2] ^ middle[i+3] ^ self.round_key[31-i]),2)
            middle[i+4] = middle[i] ^ temp
        
        result = ''
        for i in range(35, 31, -1):
            result += '%08x' % middle[i]
        
        return bytes.fromhex(result)


if __name__ == "__main__":
    a = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
    s = SM4Crypto(a)
    b = s.encryption(a)
    print(b.hex())

    
            
        