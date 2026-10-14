0000000000001230 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1230:	mov    (%rsi),%rax
    1233:	mov    0x8(%rsi),%rcx
    1237:	sub    %rax,%rcx
    123a:	je     127e <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    123c:	sar    $0x2,%rcx
    1240:	mov    (%rdi),%rdx
    1243:	mov    0x8(%rdi),%rsi
    1247:	sub    %rdx,%rsi
    124a:	sar    $0x2,%rsi
    124e:	lea    -0x1(%rcx),%rdi
    1252:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1260:	cmp    %rsi,%rdi
    1263:	jae    127f <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4f>
    1265:	mov    -0x4(%rax,%rcx,4),%r8d
    126a:	add    %r8d,%r8d
    126d:	mov    %r8d,-0x4(%rdx,%rcx,4)
    1272:	lea    -0x1(%rcx),%r8
    1276:	mov    %r8,%rcx
    1279:	test   %r8,%r8
    127c:	jne    1260 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    127e:	ret
    127f:	ud2
    1281:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
