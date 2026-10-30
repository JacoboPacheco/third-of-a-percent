0000000000001240 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
    1240:	test   %rsi,%rsi
    1243:	je     1298 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x58>
    1245:	mov    (%rdi),%rax
    1248:	mov    0x8(%rdi),%rcx
    124c:	sub    %rax,%rcx
    124f:	sar    $0x2,%rcx
    1253:	lea    -0x1(%rsi),%r8
    1257:	xor    %r9d,%r9d
    125a:	xor    %edi,%edi
    125c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    126b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    127a:	nopw   0x0(%rax,%rax,1)
    1280:	cmp    %r8,%rcx
    1283:	jbe    129e <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x5e>
    1285:	movslq (%rax,%r9,4),%r10
    1289:	add    %r10,%rdi
    128c:	inc    %r9
    128f:	cmp    %r9,%rsi
    1292:	jne    1280 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x40>
    1294:	mov    %rdi,(%rdx)
    1297:	ret
    1298:	xor    %edi,%edi
    129a:	mov    %rdi,(%rdx)
    129d:	ret
    129e:	ud2
