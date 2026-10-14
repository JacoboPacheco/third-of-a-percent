0000000000001240 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     12f8 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb8>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdi),%rdx
    1257:	mov    0x8(%rdi),%rsi
    125b:	sub    %rdx,%rsi
    125e:	sar    $0x2,%rsi
    1262:	cmp    $0x1,%rcx
    1266:	adc    $0x0,%rcx
    126a:	lea    -0x1(%rcx),%r8
    126e:	cmp    %rsi,%r8
    1271:	cmovae %rsi,%r8
    1275:	xor    %edi,%edi
    1277:	cmp    $0x8,%r8
    127b:	jb     12e0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    127d:	mov    %rdx,%r9
    1280:	sub    %rax,%r9
    1283:	cmp    $0x1f,%r9
    1287:	jbe    12e0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    1289:	inc    %r8
    128c:	mov    %r8d,%edi
    128f:	and    $0x7,%edi
    1292:	mov    $0x8,%r9d
    1298:	cmovne %rdi,%r9
    129c:	mov    %r8,%rdi
    129f:	sub    %r9,%rdi
    12a2:	xor    %r8d,%r8d
    12a5:	data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	movdqu (%rax,%r8,4),%xmm0
    12b6:	movdqu 0x10(%rax,%r8,4),%xmm1
    12bd:	paddd  %xmm0,%xmm0
    12c1:	paddd  %xmm1,%xmm1
    12c5:	movdqu %xmm0,(%rdx,%r8,4)
    12cb:	movdqu %xmm1,0x10(%rdx,%r8,4)
    12d2:	add    $0x8,%r8
    12d6:	cmp    %r8,%rdi
    12d9:	jne    12b0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    12db:	nopl   0x0(%rax,%rax,1)
    12e0:	cmp    %rdi,%rsi
    12e3:	je     12f9 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    12e5:	mov    (%rax,%rdi,4),%r8d
    12e9:	add    %r8d,%r8d
    12ec:	mov    %r8d,(%rdx,%rdi,4)
    12f0:	inc    %rdi
    12f3:	cmp    %rdi,%rcx
    12f6:	jne    12e0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12f8:	ret
    12f9:	ud2
    12fb:	nopl   0x0(%rax,%rax,1)
