0000000000001220 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1220:	test   %rcx,%rcx
    1223:	je     143a <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x21a>
    1229:	push   %rbp
    122a:	push   %r15
    122c:	push   %r14
    122e:	push   %r13
    1230:	push   %r12
    1232:	push   %rbx
    1233:	mov    (%rsi),%rax
    1236:	mov    %rax,-0x10(%rsp)
    123b:	mov    (%rdx),%rdx
    123e:	mov    (%rdi),%r12
    1241:	lea    0x0(,%rcx,4),%rdi
    1249:	mov    %rcx,%rax
    124c:	imul   %rcx,%rax
    1250:	lea    (%rdx,%rax,4),%rax
    1254:	mov    %rax,-0x28(%rsp)
    1259:	lea    (%r12,%rcx,4),%rax
    125d:	mov    %rax,-0x30(%rsp)
    1262:	mov    %rcx,%r10
    1265:	and    $0xffffffffffffffe0,%r10
    1269:	mov    %ecx,%eax
    126b:	and    $0x3,%eax
    126e:	mov    %rax,-0x40(%rsp)
    1273:	mov    %rdx,-0x18(%rsp)
    1278:	lea    0x60(%rdx),%rax
    127c:	mov    %rax,-0x38(%rsp)
    1281:	lea    0x60(%r12),%r14
    1286:	xor    %r8d,%r8d
    1289:	mov    %r12,-0x20(%rsp)
    128e:	jmp    12a7 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x87>
    1290:	mov    -0x8(%rsp),%r8
    1295:	inc    %r8
    1298:	add    %rdi,%r14
    129b:	add    %rdi,%r12
    129e:	cmp    %rcx,%r8
    12a1:	je     1430 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x210>
    12a7:	test   %rdi,%rdi
    12aa:	sets   %al
    12ad:	mov    %rdi,%rdx
    12b0:	imul   %r8,%rdx
    12b4:	mov    -0x20(%rsp),%rsi
    12b9:	add    %rdx,%rsi
    12bc:	add    -0x30(%rsp),%rdx
    12c1:	mov    %r8,-0x8(%rsp)
    12c6:	imul   %rcx,%r8
    12ca:	mov    -0x10(%rsp),%r9
    12cf:	lea    (%r9,%r8,4),%r13
    12d3:	cmp    -0x28(%rsp),%rsi
    12d8:	setb   %sil
    12dc:	mov    -0x18(%rsp),%r8
    12e1:	cmp    %rdx,%r8
    12e4:	setb   %bpl
    12e8:	and    %sil,%bpl
    12eb:	or     %al,%bpl
    12ee:	mov    %r8,%rdx
    12f1:	mov    -0x38(%rsp),%rbx
    12f6:	xor    %r9d,%r9d
    12f9:	jmp    130e <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xee>
    12fb:	nopl   0x0(%rax,%rax,1)
    1300:	inc    %r9
    1303:	add    %rdi,%rbx
    1306:	add    %rdi,%rdx
    1309:	cmp    %rcx,%r9
    130c:	je     1290 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    130e:	cmp    $0x20,%rcx
    1312:	setb   %al
    1315:	mov    0x0(%r13,%r9,4),%r8d
    131a:	or     %bpl,%al
    131d:	je     1330 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x110>
    131f:	xor    %eax,%eax
    1321:	jmp    13a6 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x186>
    1326:	cs nopw 0x0(%rax,%rax,1)
    1330:	vmovd  %r8d,%xmm0
    1335:	vpbroadcastd %xmm0,%ymm0
    133a:	xor    %eax,%eax
    133c:	nopl   0x0(%rax)
    1340:	vpmulld -0x60(%rbx,%rax,4),%ymm0,%ymm1
    1347:	vpmulld -0x40(%rbx,%rax,4),%ymm0,%ymm2
    134e:	vpmulld -0x20(%rbx,%rax,4),%ymm0,%ymm3
    1355:	vpmulld (%rbx,%rax,4),%ymm0,%ymm4
    135b:	vpaddd -0x60(%r14,%rax,4),%ymm1,%ymm1
    1362:	vpaddd -0x40(%r14,%rax,4),%ymm2,%ymm2
    1369:	vpaddd -0x20(%r14,%rax,4),%ymm3,%ymm3
    1370:	vpaddd (%r14,%rax,4),%ymm4,%ymm4
    1376:	vmovdqu %ymm1,-0x60(%r14,%rax,4)
    137d:	vmovdqu %ymm2,-0x40(%r14,%rax,4)
    1384:	vmovdqu %ymm3,-0x20(%r14,%rax,4)
    138b:	vmovdqu %ymm4,(%r14,%rax,4)
    1391:	add    $0x20,%rax
    1395:	cmp    %rax,%r10
    1398:	jne    1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x120>
    139a:	mov    %r10,%rax
    139d:	cmp    %rcx,%r10
    13a0:	je     1300 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xe0>
    13a6:	mov    %rax,%rsi
    13a9:	cmpq   $0x0,-0x40(%rsp)
    13af:	je     13d4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1b4>
    13b1:	mov    -0x40(%rsp),%r11
    13b6:	mov    %rax,%rsi
    13b9:	nopl   0x0(%rax)
    13c0:	mov    (%rdx,%rsi,4),%r15d
    13c4:	imul   %r8d,%r15d
    13c8:	add    %r15d,(%r12,%rsi,4)
    13cc:	inc    %rsi
    13cf:	dec    %r11
    13d2:	jne    13c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1a0>
    13d4:	sub    %rcx,%rax
    13d7:	cmp    $0xfffffffffffffffc,%rax
    13db:	ja     1300 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xe0>
    13e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13f0:	mov    (%rdx,%rsi,4),%eax
    13f3:	imul   %r8d,%eax
    13f7:	add    %eax,(%r12,%rsi,4)
    13fb:	mov    0x4(%rdx,%rsi,4),%eax
    13ff:	imul   %r8d,%eax
    1403:	add    %eax,0x4(%r12,%rsi,4)
    1408:	mov    0x8(%rdx,%rsi,4),%eax
    140c:	imul   %r8d,%eax
    1410:	add    %eax,0x8(%r12,%rsi,4)
    1415:	mov    0xc(%rdx,%rsi,4),%eax
    1419:	imul   %r8d,%eax
    141d:	add    %eax,0xc(%r12,%rsi,4)
    1422:	add    $0x4,%rsi
    1426:	cmp    %rsi,%rcx
    1429:	jne    13f0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1d0>
    142b:	jmp    1300 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xe0>
    1430:	pop    %rbx
    1431:	pop    %r12
    1433:	pop    %r13
    1435:	pop    %r14
    1437:	pop    %r15
    1439:	pop    %rbp
    143a:	vzeroupper
    143d:	ret
    143e:	xchg   %ax,%ax
