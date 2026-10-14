0000000000001220 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1264 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x44>
    122c:	sar    $0x2,%rcx
    1230:	mov    (%rsi),%rdx
    1233:	mov    0x8(%rsi),%rsi
    1237:	sub    %rdx,%rsi
    123a:	sar    $0x2,%rsi
    123e:	xor    %edi,%edi
    1240:	cmp    %rsi,%rdi
    1243:	jae    1265 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x45>
    1245:	lea    0x1(%rdi),%r8
    1249:	cmp    %rsi,%r8
    124c:	jae    1265 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x45>
    124e:	mov    0x4(%rdx,%rdi,4),%r8d
    1253:	add    (%rdx,%rdi,4),%r8d
    1257:	mov    %r8d,(%rax,%rdi,2)
    125b:	add    $0x2,%rdi
    125f:	dec    %rcx
    1262:	jne    1240 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x20>
    1264:	ret
    1265:	ud2
    1267:	nopw   0x0(%rax,%rax,1)
