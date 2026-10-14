0000000000001280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	push   %rbx
    1281:	mov    (%rdx),%rcx
    1284:	mov    0x8(%rdx),%rdx
    1288:	mov    %rdx,%r8
    128b:	sub    %rcx,%r8
    128e:	mov    (%rdi),%rax
    1291:	mov    0x8(%rdi),%rdi
    1295:	sub    %rax,%rdi
    1298:	cmp    %r8,%rdi
    129b:	jb     136b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xeb>
    12a1:	cmp    %rcx,%rdx
    12a4:	je     1369 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe9>
    12aa:	mov    (%rsi),%rdx
    12ad:	mov    0x8(%rsi),%rsi
    12b1:	cmp    %rsi,%rdx
    12b4:	je     136b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xeb>
    12ba:	sar    $0x2,%r8
    12be:	sub    %rdx,%rsi
    12c1:	sar    $0x2,%rsi
    12c5:	dec    %rsi
    12c8:	mov    $0x1,%r9d
    12ce:	cmp    $0x2,%r8
    12d2:	cmovae %r8,%r9
    12d6:	jae    12df <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    12d8:	xor    %edi,%edi
    12da:	xor    %r8d,%r8d
    12dd:	jmp    1342 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc2>
    12df:	mov    %r9,%r10
    12e2:	and    $0xfffffffffffffffe,%r10
    12e6:	xor    %edi,%edi
    12e8:	xor    %r8d,%r8d
    12eb:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fa:	nopw   0x0(%rax,%rax,1)
    1300:	mov    (%rcx,%r8,4),%r11d
    1304:	xor    %ebx,%ebx
    1306:	cmp    %r11,%rsi
    1309:	setb   %bl
    130c:	cmovb  %rsi,%r11
    1310:	or     %rdi,%rbx
    1313:	mov    (%rdx,%r11,4),%edi
    1317:	mov    %edi,(%rax,%r8,4)
    131b:	mov    0x4(%rcx,%r8,4),%r11d
    1320:	xor    %edi,%edi
    1322:	cmp    %r11,%rsi
    1325:	setb   %dil
    1329:	cmovb  %rsi,%r11
    132d:	or     %rbx,%rdi
    1330:	mov    (%rdx,%r11,4),%r11d
    1334:	mov    %r11d,0x4(%rax,%r8,4)
    1339:	add    $0x2,%r8
    133d:	cmp    %r8,%r10
    1340:	jne    1300 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    1342:	test   $0x1,%r9b
    1346:	je     1364 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe4>
    1348:	mov    (%rcx,%r8,4),%ecx
    134c:	xor    %r9d,%r9d
    134f:	cmp    %rcx,%rsi
    1352:	cmovb  %rsi,%rcx
    1356:	setb   %r9b
    135a:	or     %r9,%rdi
    135d:	mov    (%rdx,%rcx,4),%ecx
    1360:	mov    %ecx,(%rax,%r8,4)
    1364:	test   %rdi,%rdi
    1367:	jne    136b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xeb>
    1369:	pop    %rbx
    136a:	ret
    136b:	ud2
    136d:	nopl   (%rax)
