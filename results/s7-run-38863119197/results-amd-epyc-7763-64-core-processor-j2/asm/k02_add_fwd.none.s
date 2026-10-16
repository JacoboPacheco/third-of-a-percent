0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1361 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rdx),%rdx
    1237:	mov    (%rdi),%rsi
    123a:	cmp    $0x1,%rcx
    123e:	mov    %rcx,%rdi
    1241:	adc    $0x0,%rdi
    1245:	cmp    $0xc,%rcx
    1249:	jae    12e4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    124f:	xor    %r8d,%r8d
    1252:	mov    %rdi,%r10
    1255:	mov    %r8,%r9
    1258:	and    $0x3,%r10
    125c:	je     1284 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>
    125e:	mov    %r8,%r9
    1261:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1270:	mov    (%rdx,%r9,4),%r11d
    1274:	add    (%rax,%r9,4),%r11d
    1278:	mov    %r11d,(%rsi,%r9,4)
    127c:	inc    %r9
    127f:	dec    %r10
    1282:	jne    1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    1284:	sub    %rdi,%r8
    1287:	cmp    $0xfffffffffffffffc,%r8
    128b:	ja     1361 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1291:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a0:	mov    (%rdx,%r9,4),%edi
    12a4:	add    (%rax,%r9,4),%edi
    12a8:	mov    %edi,(%rsi,%r9,4)
    12ac:	mov    0x4(%rdx,%r9,4),%edi
    12b1:	add    0x4(%rax,%r9,4),%edi
    12b6:	mov    %edi,0x4(%rsi,%r9,4)
    12bb:	mov    0x8(%rdx,%r9,4),%edi
    12c0:	add    0x8(%rax,%r9,4),%edi
    12c5:	mov    %edi,0x8(%rsi,%r9,4)
    12ca:	mov    0xc(%rdx,%r9,4),%edi
    12cf:	add    0xc(%rax,%r9,4),%edi
    12d4:	mov    %edi,0xc(%rsi,%r9,4)
    12d9:	add    $0x4,%r9
    12dd:	cmp    %r9,%rcx
    12e0:	jne    12a0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12e2:	jmp    1361 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    12e4:	mov    %rsi,%r9
    12e7:	sub    %rax,%r9
    12ea:	xor    %r8d,%r8d
    12ed:	cmp    $0x20,%r9
    12f1:	jb     1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    12f7:	mov    %rsi,%r9
    12fa:	sub    %rdx,%r9
    12fd:	cmp    $0x20,%r9
    1301:	jb     1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1307:	mov    %rdi,%r8
    130a:	and    $0xfffffffffffffff8,%r8
    130e:	xor    %r9d,%r9d
    1311:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1320:	movdqu (%rax,%r9,4),%xmm0
    1326:	movdqu 0x10(%rax,%r9,4),%xmm1
    132d:	movdqu (%rdx,%r9,4),%xmm2
    1333:	paddd  %xmm0,%xmm2
    1337:	movdqu 0x10(%rdx,%r9,4),%xmm0
    133e:	paddd  %xmm1,%xmm0
    1342:	movdqu %xmm2,(%rsi,%r9,4)
    1348:	movdqu %xmm0,0x10(%rsi,%r9,4)
    134f:	add    $0x8,%r9
    1353:	cmp    %r9,%r8
    1356:	jne    1320 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    1358:	cmp    %r8,%rdi
    135b:	jne    1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1361:	ret
    1362:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
