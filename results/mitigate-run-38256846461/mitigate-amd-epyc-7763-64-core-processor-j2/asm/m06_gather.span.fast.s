0000000000001240 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rdx),%rax
    1243:	mov    0x8(%rdx),%r8
    1247:	mov    %r8,%rcx
    124a:	sub    %rax,%rcx
    124d:	mov    (%rdi),%rdx
    1250:	mov    0x8(%rdi),%rdi
    1254:	sub    %rdx,%rdi
    1257:	cmp    %rcx,%rdi
    125a:	jb     129a <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5a>
    125c:	cmp    %rax,%r8
    125f:	je     1299 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x59>
    1261:	sar    $0x2,%rcx
    1265:	mov    (%rsi),%rdi
    1268:	mov    0x8(%rsi),%rsi
    126c:	sub    %rdi,%rsi
    126f:	sar    $0x2,%rsi
    1273:	cmp    $0x1,%rcx
    1277:	adc    $0x0,%rcx
    127b:	xor    %r8d,%r8d
    127e:	xchg   %ax,%ax
    1280:	movslq (%rax,%r8,4),%r9
    1284:	cmp    %r9,%rsi
    1287:	jbe    129a <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5a>
    1289:	mov    (%rdi,%r9,4),%r9d
    128d:	mov    %r9d,(%rdx,%r8,4)
    1291:	inc    %r8
    1294:	cmp    %r8,%rcx
    1297:	jne    1280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    1299:	ret
    129a:	ud2
    129c:	nopl   0x0(%rax)
