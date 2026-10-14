0000000000001220 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%rdx
    1227:	sub    %rax,%rdx
    122a:	je     1284 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>
    122c:	mov    (%rsi),%rcx
    122f:	cmp    $0x4,%rdx
    1233:	jne    1239 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x19>
    1235:	xor    %esi,%esi
    1237:	jmp    1275 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x55>
    1239:	mov    %rdx,%rdi
    123c:	sar    $0x2,%rdi
    1240:	and    $0xfffffffffffffffe,%rdi
    1244:	xor    %esi,%esi
    1246:	cs nopw 0x0(%rax,%rax,1)
    1250:	mov    0x4(%rcx,%rsi,8),%r8d
    1255:	add    (%rcx,%rsi,8),%r8d
    1259:	mov    %r8d,(%rax,%rsi,4)
    125d:	mov    0xc(%rcx,%rsi,8),%r8d
    1262:	add    0x8(%rcx,%rsi,8),%r8d
    1267:	mov    %r8d,0x4(%rax,%rsi,4)
    126c:	add    $0x2,%rsi
    1270:	cmp    %rsi,%rdi
    1273:	jne    1250 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    1275:	test   $0x4,%dl
    1278:	je     1284 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>
    127a:	mov    0x4(%rcx,%rsi,8),%edx
    127e:	add    (%rcx,%rsi,8),%edx
    1281:	mov    %edx,(%rax,%rsi,4)
    1284:	ret
    1285:	data16 cs nopw 0x0(%rax,%rax,1)
