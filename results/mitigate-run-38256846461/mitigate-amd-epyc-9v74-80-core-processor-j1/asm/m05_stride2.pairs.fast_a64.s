0000000000001280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rdi),%rax
    1283:	mov    0x8(%rdi),%rdi
    1287:	mov    %rdi,%rcx
    128a:	sub    %rax,%rcx
    128d:	sar    $0x2,%rcx
    1291:	mov    (%rsi),%rdx
    1294:	mov    0x8(%rsi),%rsi
    1298:	sub    %rdx,%rsi
    129b:	sar    $0x2,%rsi
    129f:	mov    %rsi,%r8
    12a2:	shr    $1,%r8
    12a5:	cmp    %rcx,%r8
    12a8:	jb     12e7 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x67>
    12aa:	cmp    %rax,%rdi
    12ad:	je     12e6 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x66>
    12af:	cmp    $0x1,%rcx
    12b3:	adc    $0x0,%rcx
    12b7:	xor    %edi,%edi
    12b9:	nopl   0x0(%rax)
    12c0:	cmp    %rdi,%rsi
    12c3:	jbe    12e7 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x67>
    12c5:	lea    0x1(%rdi),%r8
    12c9:	cmp    %r8,%rsi
    12cc:	jbe    12e7 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x67>
    12ce:	mov    0x4(%rdx,%rdi,4),%r9d
    12d3:	add    (%rdx,%rdi,4),%r9d
    12d7:	mov    %r9d,(%rax,%rdi,2)
    12db:	inc    %r8
    12de:	mov    %r8,%rdi
    12e1:	dec    %rcx
    12e4:	jne    12c0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12e6:	ret
    12e7:	ud2
    12e9:	nopl   0x0(%rax)
