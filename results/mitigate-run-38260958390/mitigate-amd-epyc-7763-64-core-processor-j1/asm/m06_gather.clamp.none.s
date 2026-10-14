0000000000001240 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	push   %rbx
    1241:	mov    (%rdx),%rcx
    1244:	mov    0x8(%rdx),%rdx
    1248:	mov    %rdx,%r8
    124b:	sub    %rcx,%r8
    124e:	mov    (%rdi),%rax
    1251:	mov    0x8(%rdi),%rdi
    1255:	sub    %rax,%rdi
    1258:	cmp    %r8,%rdi
    125b:	jb     131b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdb>
    1261:	cmp    %rcx,%rdx
    1264:	je     1319 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd9>
    126a:	mov    (%rsi),%rdx
    126d:	mov    0x8(%rsi),%rsi
    1271:	cmp    %rsi,%rdx
    1274:	je     131b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdb>
    127a:	sar    $0x2,%r8
    127e:	sub    %rdx,%rsi
    1281:	sar    $0x2,%rsi
    1285:	dec    %rsi
    1288:	mov    $0x1,%r9d
    128e:	cmp    $0x2,%r8
    1292:	cmovae %r8,%r9
    1296:	jae    129f <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    1298:	xor    %edi,%edi
    129a:	xor    %r8d,%r8d
    129d:	jmp    12f2 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xb2>
    129f:	mov    %r9,%r10
    12a2:	and    $0xfffffffffffffffe,%r10
    12a6:	xor    %edi,%edi
    12a8:	xor    %r8d,%r8d
    12ab:	nopl   0x0(%rax,%rax,1)
    12b0:	mov    (%rcx,%r8,4),%r11d
    12b4:	xor    %ebx,%ebx
    12b6:	cmp    %r11,%rsi
    12b9:	setb   %bl
    12bc:	cmovb  %rsi,%r11
    12c0:	or     %rdi,%rbx
    12c3:	mov    (%rdx,%r11,4),%edi
    12c7:	mov    %edi,(%rax,%r8,4)
    12cb:	mov    0x4(%rcx,%r8,4),%r11d
    12d0:	xor    %edi,%edi
    12d2:	cmp    %r11,%rsi
    12d5:	setb   %dil
    12d9:	cmovb  %rsi,%r11
    12dd:	or     %rbx,%rdi
    12e0:	mov    (%rdx,%r11,4),%r11d
    12e4:	mov    %r11d,0x4(%rax,%r8,4)
    12e9:	add    $0x2,%r8
    12ed:	cmp    %r8,%r10
    12f0:	jne    12b0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x70>
    12f2:	test   $0x1,%r9b
    12f6:	je     1314 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd4>
    12f8:	mov    (%rcx,%r8,4),%ecx
    12fc:	xor    %r9d,%r9d
    12ff:	cmp    %rcx,%rsi
    1302:	cmovb  %rsi,%rcx
    1306:	setb   %r9b
    130a:	or     %r9,%rdi
    130d:	mov    (%rdx,%rcx,4),%ecx
    1310:	mov    %ecx,(%rax,%r8,4)
    1314:	test   %rdi,%rdi
    1317:	jne    131b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdb>
    1319:	pop    %rbx
    131a:	ret
    131b:	ud2
    131d:	nopl   (%rax)
