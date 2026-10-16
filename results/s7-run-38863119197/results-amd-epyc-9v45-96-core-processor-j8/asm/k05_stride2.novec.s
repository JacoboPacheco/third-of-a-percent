0000000000001220 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%rdi
    1227:	sub    %rax,%rdi
    122a:	je     1284 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>
    122c:	sar    $0x2,%rdi
    1230:	mov    (%rsi),%rcx
    1233:	mov    $0x1,%edx
    1238:	cmp    $0x2,%rdi
    123c:	cmovae %rdi,%rdx
    1240:	jae    1246 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x26>
    1242:	xor    %esi,%esi
    1244:	jmp    1275 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x55>
    1246:	mov    %rdx,%rdi
    1249:	and    $0xfffffffffffffffe,%rdi
    124d:	xor    %esi,%esi
    124f:	nop
    1250:	mov    0x4(%rcx,%rsi,8),%r8d
    1255:	add    (%rcx,%rsi,8),%r8d
    1259:	mov    %r8d,(%rax,%rsi,4)
    125d:	mov    0xc(%rcx,%rsi,8),%r8d
    1262:	add    0x8(%rcx,%rsi,8),%r8d
    1267:	mov    %r8d,0x4(%rax,%rsi,4)
    126c:	add    $0x2,%rsi
    1270:	cmp    %rsi,%rdi
    1273:	jne    1250 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    1275:	test   $0x1,%dl
    1278:	je     1284 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>
    127a:	mov    0x4(%rcx,%rsi,8),%edx
    127e:	add    (%rcx,%rsi,8),%edx
    1281:	mov    %edx,(%rax,%rsi,4)
    1284:	ret
    1285:	data16 cs nopw 0x0(%rax,%rax,1)
