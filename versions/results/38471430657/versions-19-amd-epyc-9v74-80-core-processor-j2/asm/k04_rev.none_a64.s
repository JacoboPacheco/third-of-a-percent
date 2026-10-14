0000000000001240 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rsi
    1247:	sub    %rax,%rsi
    124a:	je     13b4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    1250:	sar    $0x2,%rsi
    1254:	mov    (%rdi),%rcx
    1257:	cmp    $0x8,%rsi
    125b:	setb   %dl
    125e:	mov    %rax,%rdi
    1261:	sub    %rcx,%rdi
    1264:	cmp    $0x20,%rdi
    1268:	setb   %dil
    126c:	or     %dl,%dil
    126f:	cmp    $0x1,%dil
    1273:	jne    127a <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3a>
    1275:	mov    %rsi,%rdx
    1278:	jmp    12f4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb4>
    127a:	mov    %rsi,%rdi
    127d:	and    $0xfffffffffffffff8,%rdi
    1281:	mov    %esi,%edx
    1283:	and    $0x7,%edx
    1286:	lea    (%rax,%rsi,4),%r8
    128a:	add    $0xfffffffffffffff0,%r8
    128e:	lea    (%rcx,%rsi,4),%r9
    1292:	add    $0xfffffffffffffff0,%r9
    1296:	mov    %rdi,%r10
    1299:	neg    %r10
    129c:	xor    %r11d,%r11d
    129f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ae:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bd:	nopl   (%rax)
    12c0:	movdqu -0x10(%r8,%r11,4),%xmm0
    12c7:	movdqu (%r8,%r11,4),%xmm1
    12cd:	paddd  %xmm1,%xmm1
    12d1:	paddd  %xmm0,%xmm0
    12d5:	movdqu %xmm1,(%r9,%r11,4)
    12db:	movdqu %xmm0,-0x10(%r9,%r11,4)
    12e2:	add    $0xfffffffffffffff8,%r11
    12e6:	cmp    %r11,%r10
    12e9:	jne    12c0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12eb:	cmp    %rdi,%rsi
    12ee:	je     13b4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    12f4:	lea    -0x1(%rdx),%rdi
    12f8:	mov    %rdx,%r8
    12fb:	and    $0x3,%r8
    12ff:	je     13b5 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x175>
    1305:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1314:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1323:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1332:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	lea    -0x1(%rdx),%rsi
    1344:	mov    -0x4(%rax,%rdx,4),%r9d
    1349:	add    %r9d,%r9d
    134c:	mov    %r9d,-0x4(%rcx,%rdx,4)
    1351:	mov    %rsi,%rdx
    1354:	dec    %r8
    1357:	jne    1340 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1359:	cmp    $0x3,%rdi
    135d:	jb     13b4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    135f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    136e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137d:	nopl   (%rax)
    1380:	mov    -0x4(%rax,%rsi,4),%edx
    1384:	add    %edx,%edx
    1386:	mov    %edx,-0x4(%rcx,%rsi,4)
    138a:	mov    -0x8(%rax,%rsi,4),%edx
    138e:	add    %edx,%edx
    1390:	mov    %edx,-0x8(%rcx,%rsi,4)
    1394:	mov    -0xc(%rax,%rsi,4),%edx
    1398:	add    %edx,%edx
    139a:	mov    %edx,-0xc(%rcx,%rsi,4)
    139e:	mov    -0x10(%rax,%rsi,4),%edx
    13a2:	add    %edx,%edx
    13a4:	mov    %edx,-0x10(%rcx,%rsi,4)
    13a8:	lea    -0x4(%rsi),%rdx
    13ac:	mov    %rdx,%rsi
    13af:	test   %rdx,%rdx
    13b2:	jne    1380 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13b4:	ret
    13b5:	mov    %rdx,%rsi
    13b8:	cmp    $0x3,%rdi
    13bc:	jae    1380 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13be:	jmp    13b4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
