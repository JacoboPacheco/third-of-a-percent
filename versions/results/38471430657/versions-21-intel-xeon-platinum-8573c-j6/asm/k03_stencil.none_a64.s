0000000000001240 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%r9
    1247:	mov    %r9,%r10
    124a:	sub    %rax,%r10
    124d:	mov    %r10,%rcx
    1250:	sar    $0x2,%rcx
    1254:	cmp    $0x3,%rcx
    1258:	jb     13b7 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x177>
    125e:	mov    (%rdi),%rdx
    1261:	lea    -0x2(%rcx),%r8
    1265:	mov    $0x1,%edi
    126a:	mov    $0x2,%esi
    126f:	cmp    $0x8,%r8
    1273:	jb     1319 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd9>
    1279:	lea    0x4(%rdx),%r11
    127d:	add    %rdx,%r10
    1280:	add    $0xfffffffffffffffc,%r10
    1284:	cmp    %r9,%r11
    1287:	setb   %r9b
    128b:	cmp    %r10,%rax
    128e:	setb   %r10b
    1292:	test   %r10b,%r9b
    1295:	jne    1319 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd9>
    129b:	mov    %r8,%r9
    129e:	and    $0xfffffffffffffff8,%r9
    12a2:	lea    0x2(%r9),%rsi
    12a6:	lea    0x1(%r9),%rdi
    12aa:	xor    %r10d,%r10d
    12ad:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bc:	nopl   0x0(%rax)
    12c0:	movdqu (%rax,%r10,4),%xmm0
    12c6:	movdqu 0x4(%rax,%r10,4),%xmm1
    12cd:	paddd  %xmm0,%xmm1
    12d1:	movdqu 0x8(%rax,%r10,4),%xmm0
    12d8:	paddd  %xmm1,%xmm0
    12dc:	movdqu 0x10(%rax,%r10,4),%xmm1
    12e3:	movdqu 0x14(%rax,%r10,4),%xmm2
    12ea:	paddd  %xmm1,%xmm2
    12ee:	movdqu 0x18(%rax,%r10,4),%xmm1
    12f5:	paddd  %xmm2,%xmm1
    12f9:	movdqu %xmm0,0x4(%rdx,%r10,4)
    1300:	movdqu %xmm1,0x14(%rdx,%r10,4)
    1307:	add    $0x8,%r10
    130b:	cmp    %r10,%r9
    130e:	jne    12c0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    1310:	cmp    %r9,%r8
    1313:	je     13b7 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x177>
    1319:	mov    %ecx,%r8d
    131c:	sub    %esi,%r8d
    131f:	lea    0x1(%rsi),%r9
    1323:	test   $0x1,%r8b
    1327:	jne    1339 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf9>
    1329:	mov    %rsi,%r8
    132c:	mov    %rdi,%rsi
    132f:	cmp    %r9,%rcx
    1332:	jne    1352 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x112>
    1334:	jmp    13b7 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x177>
    1339:	mov    (%rax,%rdi,4),%r8d
    133d:	add    -0x4(%rax,%rdi,4),%r8d
    1342:	add    (%rax,%rsi,4),%r8d
    1346:	mov    %r8d,(%rdx,%rdi,4)
    134a:	mov    %r9,%r8
    134d:	cmp    %r9,%rcx
    1350:	je     13b7 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x177>
    1352:	neg    %rcx
    1355:	inc    %r8
    1358:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1367:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1376:	cs nopw 0x0(%rax,%rax,1)
    1380:	mov    (%rax,%rsi,4),%edi
    1383:	add    -0x4(%rax,%rsi,4),%edi
    1387:	add    -0x4(%rax,%r8,4),%edi
    138c:	mov    %edi,(%rdx,%rsi,4)
    138f:	mov    -0x4(%rax,%r8,4),%esi
    1394:	add    -0x8(%rax,%r8,4),%esi
    1399:	add    (%rax,%r8,4),%esi
    139d:	mov    %esi,-0x4(%rdx,%r8,4)
    13a2:	lea    (%rcx,%r8,1),%rdi
    13a6:	add    $0x2,%rdi
    13aa:	mov    %r8,%rsi
    13ad:	add    $0x2,%r8
    13b1:	cmp    $0x1,%rdi
    13b5:	jne    1380 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13b7:	ret
    13b8:	nopl   0x0(%rax,%rax,1)
