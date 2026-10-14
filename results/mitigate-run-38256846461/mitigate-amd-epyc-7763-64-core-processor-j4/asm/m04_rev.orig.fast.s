0000000000001240 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     128e <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    124c:	sar    $0x2,%rcx
    1250:	mov    (%rdi),%rdx
    1253:	mov    0x8(%rdi),%rsi
    1257:	sub    %rdx,%rsi
    125a:	sar    $0x2,%rsi
    125e:	lea    -0x1(%rcx),%rdi
    1262:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1270:	cmp    %rsi,%rdi
    1273:	jae    128f <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4f>
    1275:	mov    -0x4(%rax,%rcx,4),%r8d
    127a:	add    %r8d,%r8d
    127d:	mov    %r8d,-0x4(%rdx,%rcx,4)
    1282:	lea    -0x1(%rcx),%r8
    1286:	mov    %r8,%rcx
    1289:	test   %r8,%r8
    128c:	jne    1270 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    128e:	ret
    128f:	ud2
    1291:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
