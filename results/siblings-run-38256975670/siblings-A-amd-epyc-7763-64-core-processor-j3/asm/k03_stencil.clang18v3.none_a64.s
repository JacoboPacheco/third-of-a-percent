0000000000001240 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%r10
    1247:	mov    %r10,%r9
    124a:	sub    %rax,%r9
    124d:	mov    %r9,%rcx
    1250:	sar    $0x2,%rcx
    1254:	cmp    $0x3,%rcx
    1258:	jb     141f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1df>
    125e:	mov    (%rdi),%rdx
    1261:	lea    -0x2(%rcx),%r8
    1265:	mov    $0x1,%esi
    126a:	mov    $0x2,%edi
    126f:	cmp    $0x20,%r8
    1273:	jb     1341 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x101>
    1279:	lea    0x4(%rdx),%r11
    127d:	cmp    %r10,%r11
    1280:	jae    1292 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x52>
    1282:	add    %rdx,%r9
    1285:	add    $0xfffffffffffffffc,%r9
    1289:	cmp    %r9,%rax
    128c:	jb     1341 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x101>
    1292:	mov    %r8,%r9
    1295:	and    $0xffffffffffffffe0,%r9
    1299:	lea    0x2(%r9),%rdi
    129d:	lea    0x1(%r9),%rsi
    12a1:	xor    %r10d,%r10d
    12a4:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	vmovdqu 0x4(%rax,%r10,4),%ymm0
    12c7:	vmovdqu 0x24(%rax,%r10,4),%ymm1
    12ce:	vmovdqu 0x44(%rax,%r10,4),%ymm2
    12d5:	vmovdqu 0x64(%rax,%r10,4),%ymm3
    12dc:	vpaddd (%rax,%r10,4),%ymm0,%ymm0
    12e2:	vpaddd 0x20(%rax,%r10,4),%ymm1,%ymm1
    12e9:	vpaddd 0x40(%rax,%r10,4),%ymm2,%ymm2
    12f0:	vpaddd 0x60(%rax,%r10,4),%ymm3,%ymm3
    12f7:	vpaddd 0x8(%rax,%r10,4),%ymm0,%ymm0
    12fe:	vpaddd 0x28(%rax,%r10,4),%ymm1,%ymm1
    1305:	vpaddd 0x48(%rax,%r10,4),%ymm2,%ymm2
    130c:	vpaddd 0x68(%rax,%r10,4),%ymm3,%ymm3
    1313:	vmovdqu %ymm0,0x4(%rdx,%r10,4)
    131a:	vmovdqu %ymm1,0x24(%rdx,%r10,4)
    1321:	vmovdqu %ymm2,0x44(%rdx,%r10,4)
    1328:	vmovdqu %ymm3,0x64(%rdx,%r10,4)
    132f:	add    $0x20,%r10
    1333:	cmp    %r10,%r9
    1336:	jne    12c0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    1338:	cmp    %r9,%r8
    133b:	je     141f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1df>
    1341:	mov    %ecx,%r9d
    1344:	sub    %edi,%r9d
    1347:	mov    %rdi,%r8
    134a:	and    $0x3,%r9d
    134e:	je     13a0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x160>
    1350:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    135f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    136e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137d:	nopl   (%rax)
    1380:	mov    (%rax,%rsi,4),%r10d
    1384:	add    -0x4(%rax,%rsi,4),%r10d
    1389:	add    (%rax,%r8,4),%r10d
    138d:	mov    %r10d,(%rdx,%rsi,4)
    1391:	mov    %r8,%rsi
    1394:	inc    %r8
    1397:	dec    %r9
    139a:	jne    1380 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    139c:	lea    -0x1(%r8),%rsi
    13a0:	sub    %rcx,%rdi
    13a3:	cmp    $0xfffffffffffffffc,%rdi
    13a7:	ja     141f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1df>
    13a9:	add    $0x3,%r8
    13ad:	neg    %rcx
    13b0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13bf:	nop
    13c0:	mov    (%rax,%rsi,4),%edi
    13c3:	add    -0x4(%rax,%rsi,4),%edi
    13c7:	add    -0xc(%rax,%r8,4),%edi
    13cc:	mov    %edi,(%rdx,%rsi,4)
    13cf:	mov    -0xc(%rax,%r8,4),%esi
    13d4:	add    -0x10(%rax,%r8,4),%esi
    13d9:	add    -0x8(%rax,%r8,4),%esi
    13de:	mov    %esi,-0xc(%rdx,%r8,4)
    13e3:	mov    -0x8(%rax,%r8,4),%esi
    13e8:	add    -0xc(%rax,%r8,4),%esi
    13ed:	add    -0x4(%rax,%r8,4),%esi
    13f2:	mov    %esi,-0x8(%rdx,%r8,4)
    13f7:	mov    -0x4(%rax,%r8,4),%esi
    13fc:	add    -0x8(%rax,%r8,4),%esi
    1401:	add    (%rax,%r8,4),%esi
    1405:	mov    %esi,-0x4(%rdx,%r8,4)
    140a:	lea    (%rcx,%r8,1),%rdi
    140e:	add    $0x4,%rdi
    1412:	mov    %r8,%rsi
    1415:	add    $0x4,%r8
    1419:	cmp    $0x3,%rdi
    141d:	jne    13c0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x180>
    141f:	vzeroupper
    1422:	ret
    1423:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
