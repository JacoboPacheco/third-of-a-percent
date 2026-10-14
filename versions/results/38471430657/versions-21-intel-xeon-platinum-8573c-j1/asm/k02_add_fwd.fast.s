0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%r8
    1223:	mov    0x8(%rsi),%rax
    1227:	sub    %r8,%rax
    122a:	je     131e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xfe>
    1230:	sar    $0x2,%rax
    1234:	mov    (%rdx),%rsi
    1237:	mov    0x8(%rdx),%rcx
    123b:	sub    %rsi,%rcx
    123e:	sar    $0x2,%rcx
    1242:	mov    (%rdi),%r9
    1245:	mov    0x8(%rdi),%rdx
    1249:	sub    %r9,%rdx
    124c:	sar    $0x2,%rdx
    1250:	lea    -0x1(%rax),%rdi
    1254:	cmp    %rdx,%rdi
    1257:	cmovae %rdx,%rdi
    125b:	cmp    %rcx,%rdi
    125e:	cmovae %rcx,%rdi
    1262:	inc    %rdi
    1265:	cmp    $0x8,%rdi
    1269:	jbe    128c <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x6c>
    126b:	mov    %r9,%r10
    126e:	sub    %r8,%r10
    1271:	cmp    $0x20,%r10
    1275:	setb   %r10b
    1279:	mov    %r9,%r11
    127c:	sub    %rsi,%r11
    127f:	cmp    $0x20,%r11
    1283:	setb   %r11b
    1287:	or     %r10b,%r11b
    128a:	je     1290 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x70>
    128c:	xor    %edi,%edi
    128e:	jmp    12e8 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc8>
    1290:	mov    %edi,%r10d
    1293:	and    $0x7,%r10d
    1297:	mov    $0x8,%r11d
    129d:	cmovne %r10,%r11
    12a1:	sub    %r11,%rdi
    12a4:	xor    %r10d,%r10d
    12a7:	nopw   0x0(%rax,%rax,1)
    12b0:	movdqu (%r8,%r10,4),%xmm0
    12b6:	movdqu 0x10(%r8,%r10,4),%xmm1
    12bd:	movdqu (%rsi,%r10,4),%xmm2
    12c3:	paddd  %xmm0,%xmm2
    12c7:	movdqu 0x10(%rsi,%r10,4),%xmm0
    12ce:	paddd  %xmm1,%xmm0
    12d2:	movdqu %xmm2,(%r9,%r10,4)
    12d8:	movdqu %xmm0,0x10(%r9,%r10,4)
    12df:	add    $0x8,%r10
    12e3:	cmp    %r10,%rdi
    12e6:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12e8:	sub    %rdi,%rdx
    12eb:	sub    %rdi,%rcx
    12ee:	sub    %rdi,%rax
    12f1:	lea    (%r8,%rdi,4),%r8
    12f5:	lea    (%rsi,%rdi,4),%rsi
    12f9:	lea    (%r9,%rdi,4),%rdi
    12fd:	xor    %r9d,%r9d
    1300:	cmp    %r9,%rcx
    1303:	je     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xff>
    1305:	cmp    %r9,%rdx
    1308:	je     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xff>
    130a:	mov    (%rsi,%r9,4),%r10d
    130e:	add    (%r8,%r9,4),%r10d
    1312:	mov    %r10d,(%rdi,%r9,4)
    1316:	inc    %r9
    1319:	cmp    %r9,%rax
    131c:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe0>
    131e:	ret
    131f:	ud2
    1321:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
