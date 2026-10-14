0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%r8
    1223:	mov    0x8(%rsi),%rax
    1227:	sub    %r8,%rax
    122a:	je     130e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xee>
    1230:	sar    $0x2,%rax
    1234:	mov    (%rdx),%rsi
    1237:	mov    0x8(%rdx),%rcx
    123b:	sub    %rsi,%rcx
    123e:	sar    $0x2,%rcx
    1242:	mov    (%rdi),%r9
    1245:	mov    0x8(%rdi),%rdx
    1249:	sub    %r9,%rdx
    124c:	sar    $0x2,%rdx
    1250:	cmp    $0x1,%rax
    1254:	adc    $0x0,%rax
    1258:	lea    -0x1(%rax),%r10
    125c:	cmp    %rdx,%r10
    125f:	cmovae %rdx,%r10
    1263:	cmp    %rcx,%r10
    1266:	cmovae %rcx,%r10
    126a:	cmp    $0x7,%r10
    126e:	ja     1274 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>
    1270:	xor    %edi,%edi
    1272:	jmp    12cf <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    1274:	mov    %r9,%r11
    1277:	sub    %r8,%r11
    127a:	xor    %edi,%edi
    127c:	cmp    $0x10,%r11
    1280:	jb     12cf <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    1282:	mov    %r9,%r11
    1285:	sub    %rsi,%r11
    1288:	cmp    $0x10,%r11
    128c:	jb     12cf <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    128e:	inc    %r10
    1291:	mov    %r10d,%edi
    1294:	and    $0x3,%edi
    1297:	mov    $0x4,%r11d
    129d:	cmovne %rdi,%r11
    12a1:	mov    %r10,%rdi
    12a4:	sub    %r11,%rdi
    12a7:	xor    %r10d,%r10d
    12aa:	nopw   0x0(%rax,%rax,1)
    12b0:	movdqu (%r8,%r10,4),%xmm0
    12b6:	movdqu (%rsi,%r10,4),%xmm1
    12bc:	paddd  %xmm0,%xmm1
    12c0:	movdqu %xmm1,(%r9,%r10,4)
    12c6:	add    $0x4,%r10
    12ca:	cmp    %r10,%rdi
    12cd:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12cf:	sub    %rdi,%rdx
    12d2:	sub    %rdi,%rcx
    12d5:	sub    %rdi,%rax
    12d8:	lea    (%r8,%rdi,4),%r8
    12dc:	lea    (%rsi,%rdi,4),%rsi
    12e0:	lea    (%r9,%rdi,4),%rdi
    12e4:	xor    %r9d,%r9d
    12e7:	nopw   0x0(%rax,%rax,1)
    12f0:	cmp    %r9,%rcx
    12f3:	je     130f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    12f5:	cmp    %r9,%rdx
    12f8:	je     130f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    12fa:	mov    (%rsi,%r9,4),%r10d
    12fe:	add    (%r8,%r9,4),%r10d
    1302:	mov    %r10d,(%rdi,%r9,4)
    1306:	inc    %r9
    1309:	cmp    %r9,%rax
    130c:	jne    12f0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    130e:	ret
    130f:	ud2
    1311:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
