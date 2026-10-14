0000000000001280 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rsi),%rax
    1283:	mov    0x8(%rsi),%rcx
    1287:	sub    %rax,%rcx
    128a:	je     12de <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5e>
    128c:	sar    $0x2,%rcx
    1290:	mov    (%rdi),%rdx
    1293:	mov    0x8(%rdi),%rsi
    1297:	sub    %rdx,%rsi
    129a:	sar    $0x2,%rsi
    129e:	lea    -0x1(%rcx),%rdi
    12a2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	cmp    %rsi,%rdi
    12c3:	jae    12df <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5f>
    12c5:	mov    -0x4(%rax,%rcx,4),%r8d
    12ca:	add    %r8d,%r8d
    12cd:	mov    %r8d,-0x4(%rdx,%rcx,4)
    12d2:	lea    -0x1(%rcx),%r8
    12d6:	mov    %r8,%rcx
    12d9:	test   %r8,%r8
    12dc:	jne    12c0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12de:	ret
    12df:	ud2
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
