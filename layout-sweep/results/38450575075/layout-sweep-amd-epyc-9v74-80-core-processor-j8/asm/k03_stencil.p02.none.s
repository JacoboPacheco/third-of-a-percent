0000000000001240 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%r10
    1247:	mov    %r10,%r9
    124a:	sub    %rax,%r9
    124d:	mov    %r9,%rcx
    1250:	sar    $0x2,%rcx
    1254:	cmp    $0x3,%rcx
    1258:	jb     1377 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    125e:	mov    (%rdi),%rdx
    1261:	lea    -0x2(%rcx),%r8
    1265:	mov    $0x1,%edi
    126a:	mov    $0x2,%esi
    126f:	cmp    $0x8,%r8
    1273:	jb     12f9 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    1279:	lea    0x4(%rdx),%r11
    127d:	cmp    %r10,%r11
    1280:	jae    128e <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    1282:	add    %rdx,%r9
    1285:	add    $0xfffffffffffffffc,%r9
    1289:	cmp    %r9,%rax
    128c:	jb     12f9 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    128e:	mov    %r8,%r9
    1291:	and    $0xfffffffffffffff8,%r9
    1295:	lea    0x2(%r9),%rsi
    1299:	lea    0x1(%r9),%rdi
    129d:	xor    %r10d,%r10d
    12a0:	movdqu (%rax,%r10,4),%xmm0
    12a6:	movdqu 0x4(%rax,%r10,4),%xmm1
    12ad:	paddd  %xmm0,%xmm1
    12b1:	movdqu 0x8(%rax,%r10,4),%xmm0
    12b8:	paddd  %xmm1,%xmm0
    12bc:	movdqu 0x10(%rax,%r10,4),%xmm1
    12c3:	movdqu 0x14(%rax,%r10,4),%xmm2
    12ca:	paddd  %xmm1,%xmm2
    12ce:	movdqu 0x18(%rax,%r10,4),%xmm1
    12d5:	paddd  %xmm2,%xmm1
    12d9:	movdqu %xmm0,0x4(%rdx,%r10,4)
    12e0:	movdqu %xmm1,0x14(%rdx,%r10,4)
    12e7:	add    $0x8,%r10
    12eb:	cmp    %r10,%r9
    12ee:	jne    12a0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    12f0:	cmp    %r9,%r8
    12f3:	je     1377 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    12f9:	mov    %ecx,%r8d
    12fc:	sub    %esi,%r8d
    12ff:	lea    0x1(%rsi),%r9
    1303:	test   $0x1,%r8b
    1307:	jne    1316 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd6>
    1309:	mov    %rsi,%r8
    130c:	mov    %rdi,%rsi
    130f:	cmp    %r9,%rcx
    1312:	jne    132f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xef>
    1314:	jmp    1377 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1316:	mov    (%rax,%rdi,4),%r8d
    131a:	add    -0x4(%rax,%rdi,4),%r8d
    131f:	add    (%rax,%rsi,4),%r8d
    1323:	mov    %r8d,(%rdx,%rdi,4)
    1327:	mov    %r9,%r8
    132a:	cmp    %r9,%rcx
    132d:	je     1377 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    132f:	neg    %rcx
    1332:	inc    %r8
    1335:	data16 cs nopw 0x0(%rax,%rax,1)
    1340:	mov    (%rax,%rsi,4),%edi
    1343:	add    -0x4(%rax,%rsi,4),%edi
    1347:	add    -0x4(%rax,%r8,4),%edi
    134c:	mov    %edi,(%rdx,%rsi,4)
    134f:	mov    -0x4(%rax,%r8,4),%esi
    1354:	add    -0x8(%rax,%r8,4),%esi
    1359:	add    (%rax,%r8,4),%esi
    135d:	mov    %esi,-0x4(%rdx,%r8,4)
    1362:	lea    (%rcx,%r8,1),%rdi
    1366:	add    $0x2,%rdi
    136a:	mov    %r8,%rsi
    136d:	add    $0x2,%r8
    1371:	cmp    $0x1,%rdi
    1375:	jne    1340 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1377:	ret
    1378:	nopl   0x0(%rax,%rax,1)
