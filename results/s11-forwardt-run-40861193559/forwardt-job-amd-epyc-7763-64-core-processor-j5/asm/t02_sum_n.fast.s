0000000000001220 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
    1220:	test   %rsi,%rsi
    1223:	je     1258 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x38>
    1225:	mov    (%rdi),%rax
    1228:	mov    0x8(%rdi),%rcx
    122c:	sub    %rax,%rcx
    122f:	sar    $0x2,%rcx
    1233:	lea    -0x1(%rsi),%r8
    1237:	xor    %r9d,%r9d
    123a:	xor    %edi,%edi
    123c:	nopl   0x0(%rax)
    1240:	cmp    %r8,%rcx
    1243:	jbe    125e <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x3e>
    1245:	movslq (%rax,%r9,4),%r10
    1249:	add    %r10,%rdi
    124c:	inc    %r9
    124f:	cmp    %r9,%rsi
    1252:	jne    1240 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x20>
    1254:	mov    %rdi,(%rdx)
    1257:	ret
    1258:	xor    %edi,%edi
    125a:	mov    %rdi,(%rdx)
    125d:	ret
    125e:	ud2
