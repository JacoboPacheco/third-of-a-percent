0000000000001220 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rdx),%rcx
    1223:	mov    0x8(%rdx),%r9
    1227:	sub    %rcx,%r9
    122a:	je     12c4 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa4>
    1230:	sar    $0x2,%r9
    1234:	mov    (%rsi),%rax
    1237:	cmp    $0x1,%r9
    123b:	mov    %r9,%r8
    123e:	adc    $0x0,%r8
    1242:	mov    (%rdi),%rsi
    1245:	mov    %r8d,%edx
    1248:	and    $0x3,%edx
    124b:	cmp    $0x4,%r9
    124f:	jae    1255 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x35>
    1251:	xor    %edi,%edi
    1253:	jmp    129f <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x7f>
    1255:	and    $0xfffffffffffffffc,%r8
    1259:	xor    %edi,%edi
    125b:	nopl   0x0(%rax,%rax,1)
    1260:	movslq (%rcx,%rdi,4),%r9
    1264:	mov    (%rax,%r9,4),%r9d
    1268:	mov    %r9d,(%rsi,%rdi,4)
    126c:	movslq 0x4(%rcx,%rdi,4),%r9
    1271:	mov    (%rax,%r9,4),%r9d
    1275:	mov    %r9d,0x4(%rsi,%rdi,4)
    127a:	movslq 0x8(%rcx,%rdi,4),%r9
    127f:	mov    (%rax,%r9,4),%r9d
    1283:	mov    %r9d,0x8(%rsi,%rdi,4)
    1288:	movslq 0xc(%rcx,%rdi,4),%r9
    128d:	mov    (%rax,%r9,4),%r9d
    1291:	mov    %r9d,0xc(%rsi,%rdi,4)
    1296:	add    $0x4,%rdi
    129a:	cmp    %rdi,%r8
    129d:	jne    1260 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    129f:	test   %rdx,%rdx
    12a2:	je     12c4 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa4>
    12a4:	lea    (%rsi,%rdi,4),%rsi
    12a8:	lea    (%rcx,%rdi,4),%rcx
    12ac:	xor    %edi,%edi
    12ae:	xchg   %ax,%ax
    12b0:	movslq (%rcx,%rdi,4),%r8
    12b4:	mov    (%rax,%r8,4),%r8d
    12b8:	mov    %r8d,(%rsi,%rdi,4)
    12bc:	inc    %rdi
    12bf:	cmp    %rdi,%rdx
    12c2:	jne    12b0 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12c4:	ret
    12c5:	data16 cs nopw 0x0(%rax,%rax,1)
