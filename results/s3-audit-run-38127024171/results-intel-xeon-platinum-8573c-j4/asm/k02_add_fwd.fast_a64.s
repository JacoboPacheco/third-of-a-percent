0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%r8
    1243:	mov    0x8(%rsi),%rax
    1247:	sub    %r8,%rax
    124a:	je     135e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x11e>
    1250:	sar    $0x2,%rax
    1254:	mov    (%rdx),%rsi
    1257:	mov    0x8(%rdx),%rcx
    125b:	sub    %rsi,%rcx
    125e:	sar    $0x2,%rcx
    1262:	mov    (%rdi),%r9
    1265:	mov    0x8(%rdi),%rdx
    1269:	sub    %r9,%rdx
    126c:	sar    $0x2,%rdx
    1270:	cmp    $0x1,%rax
    1274:	adc    $0x0,%rax
    1278:	lea    -0x1(%rax),%r10
    127c:	cmp    %rdx,%r10
    127f:	cmovae %rdx,%r10
    1283:	cmp    %rcx,%r10
    1286:	cmovae %rcx,%r10
    128a:	cmp    $0x7,%r10
    128e:	ja     1297 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x57>
    1290:	xor    %edi,%edi
    1292:	jmp    131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    1297:	mov    %r9,%r11
    129a:	sub    %r8,%r11
    129d:	xor    %edi,%edi
    129f:	cmp    $0x10,%r11
    12a3:	jb     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    12a9:	mov    %r9,%r11
    12ac:	sub    %rsi,%r11
    12af:	cmp    $0x10,%r11
    12b3:	jb     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    12b5:	inc    %r10
    12b8:	mov    %r10d,%edi
    12bb:	and    $0x3,%edi
    12be:	mov    $0x4,%r11d
    12c4:	cmovne %rdi,%r11
    12c8:	mov    %r10,%rdi
    12cb:	sub    %r11,%rdi
    12ce:	xor    %r10d,%r10d
    12d1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ef:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fe:	xchg   %ax,%ax
    1300:	movdqu (%r8,%r10,4),%xmm0
    1306:	movdqu (%rsi,%r10,4),%xmm1
    130c:	paddd  %xmm0,%xmm1
    1310:	movdqu %xmm1,(%r9,%r10,4)
    1316:	add    $0x4,%r10
    131a:	cmp    %r10,%rdi
    131d:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    131f:	sub    %rdi,%rdx
    1322:	sub    %rdi,%rcx
    1325:	sub    %rdi,%rax
    1328:	lea    (%r8,%rdi,4),%r8
    132c:	lea    (%rsi,%rdi,4),%rsi
    1330:	lea    (%r9,%rdi,4),%rdi
    1334:	xor    %r9d,%r9d
    1337:	nopw   0x0(%rax,%rax,1)
    1340:	cmp    %r9,%rcx
    1343:	je     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x11f>
    1345:	cmp    %r9,%rdx
    1348:	je     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x11f>
    134a:	mov    (%rsi,%r9,4),%r10d
    134e:	add    (%r8,%r9,4),%r10d
    1352:	mov    %r10d,(%rdi,%r9,4)
    1356:	inc    %r9
    1359:	cmp    %r9,%rax
    135c:	jne    1340 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    135e:	ret
    135f:	ud2
    1361:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
