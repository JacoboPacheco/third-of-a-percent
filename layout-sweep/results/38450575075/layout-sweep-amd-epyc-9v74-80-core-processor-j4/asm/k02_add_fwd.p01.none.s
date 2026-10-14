0000000000001230 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1230:	mov    (%rsi),%rax
    1233:	mov    0x8(%rsi),%rcx
    1237:	sub    %rax,%rcx
    123a:	je     1371 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1240:	sar    $0x2,%rcx
    1244:	mov    (%rdx),%rdx
    1247:	mov    (%rdi),%rsi
    124a:	cmp    $0x1,%rcx
    124e:	mov    %rcx,%rdi
    1251:	adc    $0x0,%rdi
    1255:	cmp    $0xc,%rcx
    1259:	jae    12f4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    125f:	xor    %r8d,%r8d
    1262:	mov    %rdi,%r10
    1265:	mov    %r8,%r9
    1268:	and    $0x3,%r10
    126c:	je     1294 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>
    126e:	mov    %r8,%r9
    1271:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1280:	mov    (%rdx,%r9,4),%r11d
    1284:	add    (%rax,%r9,4),%r11d
    1288:	mov    %r11d,(%rsi,%r9,4)
    128c:	inc    %r9
    128f:	dec    %r10
    1292:	jne    1280 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    1294:	sub    %rdi,%r8
    1297:	cmp    $0xfffffffffffffffc,%r8
    129b:	ja     1371 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    12a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	mov    (%rdx,%r9,4),%edi
    12b4:	add    (%rax,%r9,4),%edi
    12b8:	mov    %edi,(%rsi,%r9,4)
    12bc:	mov    0x4(%rdx,%r9,4),%edi
    12c1:	add    0x4(%rax,%r9,4),%edi
    12c6:	mov    %edi,0x4(%rsi,%r9,4)
    12cb:	mov    0x8(%rdx,%r9,4),%edi
    12d0:	add    0x8(%rax,%r9,4),%edi
    12d5:	mov    %edi,0x8(%rsi,%r9,4)
    12da:	mov    0xc(%rdx,%r9,4),%edi
    12df:	add    0xc(%rax,%r9,4),%edi
    12e4:	mov    %edi,0xc(%rsi,%r9,4)
    12e9:	add    $0x4,%r9
    12ed:	cmp    %r9,%rcx
    12f0:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12f2:	jmp    1371 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    12f4:	mov    %rsi,%r9
    12f7:	sub    %rax,%r9
    12fa:	xor    %r8d,%r8d
    12fd:	cmp    $0x20,%r9
    1301:	jb     1262 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1307:	mov    %rsi,%r9
    130a:	sub    %rdx,%r9
    130d:	cmp    $0x20,%r9
    1311:	jb     1262 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1317:	mov    %rdi,%r8
    131a:	and    $0xfffffffffffffff8,%r8
    131e:	xor    %r9d,%r9d
    1321:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1330:	movdqu (%rax,%r9,4),%xmm0
    1336:	movdqu 0x10(%rax,%r9,4),%xmm1
    133d:	movdqu (%rdx,%r9,4),%xmm2
    1343:	paddd  %xmm0,%xmm2
    1347:	movdqu 0x10(%rdx,%r9,4),%xmm0
    134e:	paddd  %xmm1,%xmm0
    1352:	movdqu %xmm2,(%rsi,%r9,4)
    1358:	movdqu %xmm0,0x10(%rsi,%r9,4)
    135f:	add    $0x8,%r9
    1363:	cmp    %r9,%r8
    1366:	jne    1330 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    1368:	cmp    %r8,%rdi
    136b:	jne    1262 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1371:	ret
    1372:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
