0000000000001220 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rdx),%rax
    1223:	mov    0x8(%rdx),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     127e <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5e>
    122c:	sar    $0x2,%rcx
    1230:	mov    (%rsi),%rdx
    1233:	mov    0x8(%rsi),%rsi
    1237:	sub    %rdx,%rsi
    123a:	sar    $0x2,%rsi
    123e:	mov    (%rdi),%r8
    1241:	mov    0x8(%rdi),%rdi
    1245:	sub    %r8,%rdi
    1248:	sar    $0x2,%rdi
    124c:	cmp    $0x1,%rcx
    1250:	adc    $0x0,%rcx
    1254:	xor    %r9d,%r9d
    1257:	nopw   0x0(%rax,%rax,1)
    1260:	movslq (%rax,%r9,4),%r10
    1264:	cmp    %r10,%rsi
    1267:	jbe    127f <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    1269:	cmp    %r9,%rdi
    126c:	je     127f <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    126e:	mov    (%rdx,%r10,4),%r10d
    1272:	mov    %r10d,(%r8,%r9,4)
    1276:	inc    %r9
    1279:	cmp    %r9,%rcx
    127c:	jne    1260 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    127e:	ret
    127f:	ud2
    1281:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
