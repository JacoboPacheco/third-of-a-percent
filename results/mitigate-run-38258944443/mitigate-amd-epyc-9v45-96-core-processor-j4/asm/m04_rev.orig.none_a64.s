0000000000001280 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rsi),%rax
    1283:	mov    0x8(%rsi),%rsi
    1287:	sub    %rax,%rsi
    128a:	je     13f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    1290:	sar    $0x2,%rsi
    1294:	mov    (%rdi),%rcx
    1297:	cmp    $0x8,%rsi
    129b:	jb     1335 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb5>
    12a1:	mov    %rax,%rdx
    12a4:	sub    %rcx,%rdx
    12a7:	cmp    $0x20,%rdx
    12ab:	jb     1335 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb5>
    12b1:	mov    %rsi,%rdi
    12b4:	and    $0xfffffffffffffff8,%rdi
    12b8:	mov    %esi,%edx
    12ba:	and    $0x7,%edx
    12bd:	lea    (%rax,%rsi,4),%r8
    12c1:	add    $0xfffffffffffffff0,%r8
    12c5:	lea    (%rcx,%rsi,4),%r9
    12c9:	add    $0xfffffffffffffff0,%r9
    12cd:	mov    %rdi,%r10
    12d0:	neg    %r10
    12d3:	xor    %r11d,%r11d
    12d6:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	movdqu -0x10(%r8,%r11,4),%xmm0
    1307:	movdqu (%r8,%r11,4),%xmm1
    130d:	paddd  %xmm1,%xmm1
    1311:	paddd  %xmm0,%xmm0
    1315:	movdqu %xmm1,(%r9,%r11,4)
    131b:	movdqu %xmm0,-0x10(%r9,%r11,4)
    1322:	add    $0xfffffffffffffff8,%r11
    1326:	cmp    %r11,%r10
    1329:	jne    1300 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    132b:	cmp    %rdi,%rsi
    132e:	jne    1338 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb8>
    1330:	jmp    13f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    1335:	mov    %rsi,%rdx
    1338:	lea    -0x1(%rdx),%rdi
    133c:	mov    %rdx,%r8
    133f:	and    $0x3,%r8
    1343:	je     13f5 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x175>
    1349:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1358:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1367:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1376:	cs nopw 0x0(%rax,%rax,1)
    1380:	lea    -0x1(%rdx),%rsi
    1384:	mov    -0x4(%rax,%rdx,4),%r9d
    1389:	add    %r9d,%r9d
    138c:	mov    %r9d,-0x4(%rcx,%rdx,4)
    1391:	mov    %rsi,%rdx
    1394:	dec    %r8
    1397:	jne    1380 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1399:	cmp    $0x3,%rdi
    139d:	jb     13f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
    139f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13ae:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13bd:	nopl   (%rax)
    13c0:	mov    -0x4(%rax,%rsi,4),%edx
    13c4:	add    %edx,%edx
    13c6:	mov    %edx,-0x4(%rcx,%rsi,4)
    13ca:	mov    -0x8(%rax,%rsi,4),%edx
    13ce:	add    %edx,%edx
    13d0:	mov    %edx,-0x8(%rcx,%rsi,4)
    13d4:	mov    -0xc(%rax,%rsi,4),%edx
    13d8:	add    %edx,%edx
    13da:	mov    %edx,-0xc(%rcx,%rsi,4)
    13de:	mov    -0x10(%rax,%rsi,4),%edx
    13e2:	add    %edx,%edx
    13e4:	mov    %edx,-0x10(%rcx,%rsi,4)
    13e8:	lea    -0x4(%rsi),%rdx
    13ec:	mov    %rdx,%rsi
    13ef:	test   %rdx,%rdx
    13f2:	jne    13c0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13f4:	ret
    13f5:	mov    %rdx,%rsi
    13f8:	cmp    $0x3,%rdi
    13fc:	jae    13c0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13fe:	jmp    13f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x174>
