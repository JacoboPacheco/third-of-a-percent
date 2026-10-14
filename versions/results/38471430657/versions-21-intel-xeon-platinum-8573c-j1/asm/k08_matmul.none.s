0000000000001220 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1220:	test   %rcx,%rcx
    1223:	je     1452 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x232>
    1229:	push   %rbp
    122a:	push   %r15
    122c:	push   %r14
    122e:	push   %r13
    1230:	push   %r12
    1232:	push   %rbx
    1233:	mov    %rcx,%r14
    1236:	mov    (%rsi),%rax
    1239:	mov    %rax,-0x18(%rsp)
    123e:	mov    (%rdx),%rax
    1241:	mov    (%rdi),%r15
    1244:	lea    0x0(,%rcx,4),%rdi
    124c:	imul   %r14,%rcx
    1250:	lea    (%rax,%rcx,4),%rcx
    1254:	mov    %rcx,-0x28(%rsp)
    1259:	lea    (%r15,%r14,4),%rcx
    125d:	mov    %rcx,-0x30(%rsp)
    1262:	mov    %r14,%rcx
    1265:	and    $0xfffffffffffffff8,%rcx
    1269:	lea    0x10(%r15),%r11
    126d:	mov    %rax,-0x40(%rsp)
    1272:	add    $0x10,%rax
    1276:	mov    %rax,-0x38(%rsp)
    127b:	xor    %r9d,%r9d
    127e:	mov    %r15,-0x20(%rsp)
    1283:	jmp    12a7 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x87>
    1285:	data16 cs nopw 0x0(%rax,%rax,1)
    1290:	mov    -0x10(%rsp),%r9
    1295:	inc    %r9
    1298:	add    %rdi,%r11
    129b:	add    %rdi,%r15
    129e:	cmp    %r14,%r9
    12a1:	je     1448 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x228>
    12a7:	test   %rdi,%rdi
    12aa:	sets   %dl
    12ad:	mov    %rdi,%rsi
    12b0:	imul   %r9,%rsi
    12b4:	mov    -0x20(%rsp),%r10
    12b9:	lea    (%r10,%rsi,1),%r8
    12bd:	add    -0x30(%rsp),%rsi
    12c2:	mov    %r9,-0x10(%rsp)
    12c7:	imul   %r14,%r9
    12cb:	mov    -0x18(%rsp),%rax
    12d0:	lea    (%rax,%r9,4),%r12
    12d4:	lea    (%r10,%r9,4),%rax
    12d8:	mov    %rax,-0x8(%rsp)
    12dd:	cmp    -0x28(%rsp),%r8
    12e2:	setb   %r8b
    12e6:	mov    -0x40(%rsp),%rax
    12eb:	cmp    %rsi,%rax
    12ee:	setb   %bpl
    12f2:	and    %r8b,%bpl
    12f5:	or     %dl,%bpl
    12f8:	mov    %rax,%rdx
    12fb:	mov    -0x38(%rsp),%rbx
    1300:	xor    %eax,%eax
    1302:	jmp    1322 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x102>
    1304:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1310:	inc    %rax
    1313:	add    %rdi,%rbx
    1316:	add    %rdi,%rdx
    1319:	cmp    %r14,%rax
    131c:	je     1290 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    1322:	cmp    $0x8,%r14
    1326:	setb   %sil
    132a:	mov    (%r12,%rax,4),%r8d
    132e:	or     %bpl,%sil
    1331:	test   $0x1,%sil
    1335:	je     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x120>
    1337:	xor    %r10d,%r10d
    133a:	jmp    13da <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1ba>
    133f:	nop
    1340:	movd   %r8d,%xmm0
    1345:	pshufd $0x0,%xmm0,%xmm0
    134a:	pshufd $0xf5,%xmm0,%xmm1
    134f:	xor    %r10d,%r10d
    1352:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1360:	movdqu -0x10(%rbx,%r10,4),%xmm2
    1367:	movdqu (%rbx,%r10,4),%xmm3
    136d:	pshufd $0xf5,%xmm2,%xmm4
    1372:	pmuludq %xmm0,%xmm2
    1376:	pshufd $0xe8,%xmm2,%xmm2
    137b:	pmuludq %xmm1,%xmm4
    137f:	pshufd $0xe8,%xmm4,%xmm4
    1384:	punpckldq %xmm4,%xmm2
    1388:	pshufd $0xf5,%xmm3,%xmm4
    138d:	pmuludq %xmm0,%xmm3
    1391:	pshufd $0xe8,%xmm3,%xmm3
    1396:	pmuludq %xmm1,%xmm4
    139a:	pshufd $0xe8,%xmm4,%xmm4
    139f:	punpckldq %xmm4,%xmm3
    13a3:	movdqu -0x10(%r11,%r10,4),%xmm4
    13aa:	paddd  %xmm2,%xmm4
    13ae:	movdqu (%r11,%r10,4),%xmm2
    13b4:	paddd  %xmm3,%xmm2
    13b8:	movdqu %xmm4,-0x10(%r11,%r10,4)
    13bf:	movdqu %xmm2,(%r11,%r10,4)
    13c5:	add    $0x8,%r10
    13c9:	cmp    %r10,%rcx
    13cc:	jne    1360 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    13ce:	mov    %rcx,%r10
    13d1:	cmp    %rcx,%r14
    13d4:	je     1310 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    13da:	mov    %r10,%rsi
    13dd:	or     $0x1,%rsi
    13e1:	test   $0x1,%r14b
    13e5:	je     1413 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1f3>
    13e7:	mov    %rax,%r9
    13ea:	imul   %r14,%r9
    13ee:	mov    -0x40(%rsp),%r13
    13f3:	lea    0x0(,%r9,4),%r9
    13fb:	add    %r13,%r9
    13fe:	mov    (%r9,%r10,4),%r9d
    1402:	imul   %r8d,%r9d
    1406:	mov    -0x8(%rsp),%r13
    140b:	add    %r9d,0x0(%r13,%r10,4)
    1410:	mov    %rsi,%r10
    1413:	cmp    %rsi,%r14
    1416:	je     1310 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    141c:	nopl   0x0(%rax)
    1420:	mov    (%rdx,%r10,4),%esi
    1424:	imul   %r8d,%esi
    1428:	add    %esi,(%r15,%r10,4)
    142c:	mov    0x4(%rdx,%r10,4),%esi
    1431:	imul   %r8d,%esi
    1435:	add    %esi,0x4(%r15,%r10,4)
    143a:	add    $0x2,%r10
    143e:	cmp    %r10,%r14
    1441:	jne    1420 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    1443:	jmp    1310 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    1448:	pop    %rbx
    1449:	pop    %r12
    144b:	pop    %r13
    144d:	pop    %r14
    144f:	pop    %r15
    1451:	pop    %rbp
    1452:	ret
    1453:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
