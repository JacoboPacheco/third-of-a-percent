0000000000001240 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rdx
    1247:	sub    %rax,%rdx
    124a:	je     13d8 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x198>
    1250:	sar    $0x2,%rdx
    1254:	mov    (%rdi),%rcx
    1257:	cmp    $0x20,%rdx
    125b:	jb     1319 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd9>
    1261:	mov    %rax,%rsi
    1264:	sub    %rcx,%rsi
    1267:	cmp    $0x80,%rsi
    126e:	jb     1319 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd9>
    1274:	mov    %rdx,%rdi
    1277:	and    $0xffffffffffffffe0,%rdi
    127b:	mov    %edx,%esi
    127d:	and    $0x1f,%esi
    1280:	lea    (%rax,%rdx,4),%r8
    1284:	add    $0xffffffffffffffe0,%r8
    1288:	lea    (%rcx,%rdx,4),%r9
    128c:	add    $0xffffffffffffffe0,%r9
    1290:	mov    %rdi,%r10
    1293:	neg    %r10
    1296:	xor    %r11d,%r11d
    1299:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a8:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b7:	nopw   0x0(%rax,%rax,1)
    12c0:	vmovdqu -0x60(%r8,%r11,4),%ymm0
    12c7:	vmovdqu -0x40(%r8,%r11,4),%ymm1
    12ce:	vmovdqu -0x20(%r8,%r11,4),%ymm2
    12d5:	vmovdqu (%r8,%r11,4),%ymm3
    12db:	vpaddd %ymm3,%ymm3,%ymm3
    12df:	vpaddd %ymm2,%ymm2,%ymm2
    12e3:	vpaddd %ymm1,%ymm1,%ymm1
    12e7:	vpaddd %ymm0,%ymm0,%ymm0
    12eb:	vmovdqu %ymm3,(%r9,%r11,4)
    12f1:	vmovdqu %ymm2,-0x20(%r9,%r11,4)
    12f8:	vmovdqu %ymm1,-0x40(%r9,%r11,4)
    12ff:	vmovdqu %ymm0,-0x60(%r9,%r11,4)
    1306:	add    $0xffffffffffffffe0,%r11
    130a:	cmp    %r11,%r10
    130d:	jne    12c0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    130f:	cmp    %rdi,%rdx
    1312:	jne    131c <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xdc>
    1314:	jmp    13d8 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x198>
    1319:	mov    %rdx,%rsi
    131c:	lea    -0x1(%rsi),%rdi
    1320:	mov    %rsi,%r8
    1323:	and    $0x7,%r8
    1327:	je     1361 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x121>
    1329:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1338:	nopl   0x0(%rax,%rax,1)
    1340:	lea    -0x1(%rsi),%rdx
    1344:	mov    -0x4(%rax,%rsi,4),%r9d
    1349:	add    %r9d,%r9d
    134c:	mov    %r9d,-0x4(%rcx,%rsi,4)
    1351:	mov    %rdx,%rsi
    1354:	dec    %r8
    1357:	jne    1340 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1359:	cmp    $0x7,%rdi
    135d:	jae    136a <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x12a>
    135f:	jmp    13d8 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x198>
    1361:	mov    %rsi,%rdx
    1364:	cmp    $0x7,%rdi
    1368:	jb     13d8 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x198>
    136a:	dec    %rdx
    136d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137c:	nopl   0x0(%rax)
    1380:	mov    (%rax,%rdx,4),%esi
    1383:	add    %esi,%esi
    1385:	mov    %esi,(%rcx,%rdx,4)
    1388:	mov    -0x4(%rax,%rdx,4),%esi
    138c:	add    %esi,%esi
    138e:	mov    %esi,-0x4(%rcx,%rdx,4)
    1392:	mov    -0x8(%rax,%rdx,4),%esi
    1396:	add    %esi,%esi
    1398:	mov    %esi,-0x8(%rcx,%rdx,4)
    139c:	mov    -0xc(%rax,%rdx,4),%esi
    13a0:	add    %esi,%esi
    13a2:	mov    %esi,-0xc(%rcx,%rdx,4)
    13a6:	mov    -0x10(%rax,%rdx,4),%esi
    13aa:	add    %esi,%esi
    13ac:	mov    %esi,-0x10(%rcx,%rdx,4)
    13b0:	mov    -0x14(%rax,%rdx,4),%esi
    13b4:	add    %esi,%esi
    13b6:	mov    %esi,-0x14(%rcx,%rdx,4)
    13ba:	mov    -0x18(%rax,%rdx,4),%esi
    13be:	add    %esi,%esi
    13c0:	mov    %esi,-0x18(%rcx,%rdx,4)
    13c4:	mov    -0x1c(%rax,%rdx,4),%esi
    13c8:	add    %esi,%esi
    13ca:	mov    %esi,-0x1c(%rcx,%rdx,4)
    13ce:	add    $0xfffffffffffffff8,%rdx
    13d2:	cmp    $0xffffffffffffffff,%rdx
    13d6:	jne    1380 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13d8:	vzeroupper
    13db:	ret
    13dc:	nopl   0x0(%rax)
