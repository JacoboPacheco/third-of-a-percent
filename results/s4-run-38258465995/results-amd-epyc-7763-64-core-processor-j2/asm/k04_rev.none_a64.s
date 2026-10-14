0000000000001240 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rsi
    1247:	sub    %rax,%rsi
    124a:	je     13b4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    1250:	sar    $0x2,%rsi
    1254:	mov    (%rdi),%rcx
    1257:	cmp    $0x8,%rsi
    125b:	jb     12f5 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb5>
    1261:	mov    %rax,%rdx
    1264:	sub    %rcx,%rdx
    1267:	cmp    $0x20,%rdx
    126b:	jb     12f5 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb5>
    1271:	mov    %rsi,%rdi
    1274:	and    $0xfffffffffffffff8,%rdi
    1278:	mov    %esi,%edx
    127a:	and    $0x7,%edx
    127d:	lea    (%rax,%rsi,4),%r8
    1281:	add    $0xfffffffffffffff0,%r8
    1285:	lea    (%rcx,%rsi,4),%r9
    1289:	add    $0xfffffffffffffff0,%r9
    128d:	mov    %rdi,%r10
    1290:	neg    %r10
    1293:	xor    %r11d,%r11d
    1296:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
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
    12ee:	jne    12f8 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb8>
    12f0:	jmp    13b4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    12f5:	mov    %rsi,%rdx
    12f8:	lea    -0x1(%rdx),%rdi
    12fc:	mov    %rdx,%r8
    12ff:	and    $0x3,%r8
    1303:	je     13b5 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x175>
    1309:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1318:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1327:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1336:	cs nopw 0x0(%rax,%rax,1)
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
