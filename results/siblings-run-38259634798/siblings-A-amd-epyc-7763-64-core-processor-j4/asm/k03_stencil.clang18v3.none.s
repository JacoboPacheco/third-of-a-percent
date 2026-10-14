0000000000001220 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%r10
    1227:	mov    %r10,%r9
    122a:	sub    %rax,%r9
    122d:	mov    %r9,%rcx
    1230:	sar    $0x2,%rcx
    1234:	cmp    $0x3,%rcx
    1238:	jb     13af <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x18f>
    123e:	mov    (%rdi),%rdx
    1241:	lea    -0x2(%rcx),%r8
    1245:	mov    $0x1,%esi
    124a:	mov    $0x2,%edi
    124f:	cmp    $0x20,%r8
    1253:	jb     1311 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf1>
    1259:	lea    0x4(%rdx),%r11
    125d:	cmp    %r10,%r11
    1260:	jae    1272 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x52>
    1262:	add    %rdx,%r9
    1265:	add    $0xfffffffffffffffc,%r9
    1269:	cmp    %r9,%rax
    126c:	jb     1311 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf1>
    1272:	mov    %r8,%r9
    1275:	and    $0xffffffffffffffe0,%r9
    1279:	lea    0x2(%r9),%rdi
    127d:	lea    0x1(%r9),%rsi
    1281:	xor    %r10d,%r10d
    1284:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1290:	vmovdqu 0x4(%rax,%r10,4),%ymm0
    1297:	vmovdqu 0x24(%rax,%r10,4),%ymm1
    129e:	vmovdqu 0x44(%rax,%r10,4),%ymm2
    12a5:	vmovdqu 0x64(%rax,%r10,4),%ymm3
    12ac:	vpaddd (%rax,%r10,4),%ymm0,%ymm0
    12b2:	vpaddd 0x20(%rax,%r10,4),%ymm1,%ymm1
    12b9:	vpaddd 0x40(%rax,%r10,4),%ymm2,%ymm2
    12c0:	vpaddd 0x60(%rax,%r10,4),%ymm3,%ymm3
    12c7:	vpaddd 0x8(%rax,%r10,4),%ymm0,%ymm0
    12ce:	vpaddd 0x28(%rax,%r10,4),%ymm1,%ymm1
    12d5:	vpaddd 0x48(%rax,%r10,4),%ymm2,%ymm2
    12dc:	vpaddd 0x68(%rax,%r10,4),%ymm3,%ymm3
    12e3:	vmovdqu %ymm0,0x4(%rdx,%r10,4)
    12ea:	vmovdqu %ymm1,0x24(%rdx,%r10,4)
    12f1:	vmovdqu %ymm2,0x44(%rdx,%r10,4)
    12f8:	vmovdqu %ymm3,0x64(%rdx,%r10,4)
    12ff:	add    $0x20,%r10
    1303:	cmp    %r10,%r9
    1306:	jne    1290 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    1308:	cmp    %r9,%r8
    130b:	je     13af <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x18f>
    1311:	mov    %ecx,%r9d
    1314:	sub    %edi,%r9d
    1317:	mov    %rdi,%r8
    131a:	and    $0x3,%r9d
    131e:	je     1340 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x120>
    1320:	mov    (%rax,%rsi,4),%r10d
    1324:	add    -0x4(%rax,%rsi,4),%r10d
    1329:	add    (%rax,%r8,4),%r10d
    132d:	mov    %r10d,(%rdx,%rsi,4)
    1331:	mov    %r8,%rsi
    1334:	inc    %r8
    1337:	dec    %r9
    133a:	jne    1320 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    133c:	lea    -0x1(%r8),%rsi
    1340:	sub    %rcx,%rdi
    1343:	cmp    $0xfffffffffffffffc,%rdi
    1347:	ja     13af <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x18f>
    1349:	add    $0x3,%r8
    134d:	neg    %rcx
    1350:	mov    (%rax,%rsi,4),%edi
    1353:	add    -0x4(%rax,%rsi,4),%edi
    1357:	add    -0xc(%rax,%r8,4),%edi
    135c:	mov    %edi,(%rdx,%rsi,4)
    135f:	mov    -0xc(%rax,%r8,4),%esi
    1364:	add    -0x10(%rax,%r8,4),%esi
    1369:	add    -0x8(%rax,%r8,4),%esi
    136e:	mov    %esi,-0xc(%rdx,%r8,4)
    1373:	mov    -0x8(%rax,%r8,4),%esi
    1378:	add    -0xc(%rax,%r8,4),%esi
    137d:	add    -0x4(%rax,%r8,4),%esi
    1382:	mov    %esi,-0x8(%rdx,%r8,4)
    1387:	mov    -0x4(%rax,%r8,4),%esi
    138c:	add    -0x8(%rax,%r8,4),%esi
    1391:	add    (%rax,%r8,4),%esi
    1395:	mov    %esi,-0x4(%rdx,%r8,4)
    139a:	lea    (%rcx,%r8,1),%rdi
    139e:	add    $0x4,%rdi
    13a2:	mov    %r8,%rsi
    13a5:	add    $0x4,%r8
    13a9:	cmp    $0x3,%rdi
    13ad:	jne    1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x130>
    13af:	vzeroupper
    13b2:	ret
    13b3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
