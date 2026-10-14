0000000000001240 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rdx),%rax
    1243:	mov    0x8(%rdx),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     129e <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5e>
    124c:	sar    $0x2,%rcx
    1250:	mov    (%rsi),%rdx
    1253:	mov    0x8(%rsi),%rsi
    1257:	sub    %rdx,%rsi
    125a:	sar    $0x2,%rsi
    125e:	mov    (%rdi),%r8
    1261:	mov    0x8(%rdi),%rdi
    1265:	sub    %r8,%rdi
    1268:	sar    $0x2,%rdi
    126c:	xor    %r9d,%r9d
    126f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    127e:	xchg   %ax,%ax
    1280:	movslq (%rax,%r9,4),%r10
    1284:	cmp    %r10,%rsi
    1287:	jbe    129f <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    1289:	cmp    %r9,%rdi
    128c:	je     129f <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    128e:	mov    (%rdx,%r10,4),%r10d
    1292:	mov    %r10d,(%r8,%r9,4)
    1296:	inc    %r9
    1299:	cmp    %r9,%rcx
    129c:	jne    1280 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    129e:	ret
    129f:	ud2
    12a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
