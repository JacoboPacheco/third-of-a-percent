0000000000001220 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rdx),%rax
    1223:	mov    0x8(%rdx),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     126e <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x4e>
    122c:	sar    $0x2,%rcx
    1230:	mov    (%rsi),%rdx
    1233:	mov    0x8(%rsi),%rsi
    1237:	sub    %rdx,%rsi
    123a:	sar    $0x2,%rsi
    123e:	mov    (%rdi),%r8
    1241:	mov    0x8(%rdi),%rdi
    1245:	sub    %r8,%rdi
    1248:	sar    $0x2,%rdi
    124c:	xor    %r9d,%r9d
    124f:	nop
    1250:	movslq (%rax,%r9,4),%r10
    1254:	cmp    %r10,%rsi
    1257:	jbe    126f <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x4f>
    1259:	cmp    %r9,%rdi
    125c:	je     126f <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x4f>
    125e:	mov    (%rdx,%r10,4),%r10d
    1262:	mov    %r10d,(%r8,%r9,4)
    1266:	inc    %r9
    1269:	cmp    %r9,%rcx
    126c:	jne    1250 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x30>
    126e:	ret
    126f:	ud2
    1271:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
